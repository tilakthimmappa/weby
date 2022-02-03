from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_ec2 as ec2, aws_ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ssm as _ssm
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_logs as logs
from aws_cdk import core, aws_route53
from aws_cdk.aws_route53_targets import LoadBalancerTarget
from aws_cdk.aws_elasticloadbalancingv2 import ApplicationProtocol
from aws_cdk.aws_iam import Effect, PolicyStatement, ManagedPolicy

from .cdk_stack.event_rule_cloud import EventRuleCloudStack
from .cdk_stack.ecr_stack import ECRStack


class FargateStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, project: str, stack_vars: dict, pipeline_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        task_workers = stack_vars.pop('WORKER_ENVS', dict())
        self.stack_vars = stack_vars
        self.exec_command_policy_count = 0

        vpc = ec2.Vpc.from_vpc_attributes(self, "FargateVPC",
                                          vpc_id=stack_vars["VPC_ID"],
                                          availability_zones=stack_vars['AVAILABILITY_ZONES'].split(","),
                                          private_subnet_ids=stack_vars['PRIVATE_SUBNET_IDS'].split(","),
                                          public_subnet_ids=stack_vars['PUBLIC_SUBNET_IDS'].split(",")
                                          )

        self.fargate_cluster = ecs.Cluster(self,
                                           stack_vars["CLUSTER_NAME"],
                                           cluster_name=stack_vars["CLUSTER_NAME"],
                                           vpc=vpc)

        # ECR repo stack: ECR repo get or create and returns stack
        ecr_stack = ECRStack(scope=self, id="ECRStack", project=project, stack_vars=stack_vars,
                             pipeline_name=pipeline_name)
        ecr_repo = ecr_stack.get_or_create()

        ##Fargate Task Definitions for all apps
        app_task = ecs.FargateTaskDefinition(
            self, f"{project}-app", family=f"{project}-app-task", cpu=512,
            memory_limit_mib=1024)

        self.allow_ssm(app_task)
        self.allow_s3(app_task)
        self.allow_fargate_exec(app_task)

        app_health_check = ecs.HealthCheck(command=["CMD-SHELL", "ps ax | grep -v grep | grep puma > /dev/null"],
                                           interval=core.Duration.seconds(
                                               30),
                                           timeout=core.Duration.seconds(
                                               5),
                                           retries=3)

        log_group_obj = logs.LogGroup(self, id=f"{project}-{stack_vars['AWS_ENV_CLASSIFICATION']}",
                                      log_group_name=f"{project}-{stack_vars['AWS_ENV_CLASSIFICATION']}",
                                      retention=logs.RetentionDays.ONE_MONTH)

        app_task.add_container(f"{project}-app",
                               image=ecs.ContainerImage.from_ecr_repository(ecr_repo),
                               essential=True, environment=stack_vars,
                               logging=ecs.LogDrivers.aws_logs(stream_prefix='app', log_group=log_group_obj),
                               health_check=app_health_check) \
            .add_port_mappings(ecs.PortMapping(container_port=3000, host_port=3000, protocol=ecs.Protocol.TCP, ))

        hosted_zone = aws_route53.HostedZone.from_hosted_zone_attributes(self, "colearn.id1",
                                                                         hosted_zone_id="Z3JAHZIPXIUFDW",
                                                                         zone_name="colearn.id")

        self.app_service = ecs_patterns.ApplicationLoadBalancedFargateService(self,
                                                                              id=f"{project}-app-alb",
                                                                              service_name=f"{project}-app",
                                                                              assign_public_ip=False,
                                                                              cluster=self.fargate_cluster,
                                                                              task_definition=app_task,
                                                                              listener_port=443,
                                                                              protocol=ApplicationProtocol.HTTPS,
                                                                              domain_name=f"{stack_vars['ROUTE53_DOMAIN_RECORD']}",
                                                                              domain_zone=hosted_zone,
                                                                              certificate=acm.Certificate.from_certificate_arn(
                                                                                  self, 'domain-cert',
                                                                                  certificate_arn=f"{stack_vars['ACM_CERTIFICATE']}"),
                                                                              public_load_balancer=True,
                                                                              redirect_http=True,
                                                                              target_protocol=ApplicationProtocol.HTTP,
                                                                              task_subnets=aws_ec2.SubnetSelection(
                                                                                  subnet_type=aws_ec2.SubnetType.PRIVATE),
                                                                              )

        # creating private record set
        private_hosted_zone = aws_route53.HostedZone.from_hosted_zone_attributes(self, "private-colearn.id1",
                                                                                 hosted_zone_id="Z090253918QZPQRY38VTD",
                                                                                 zone_name="colearn.id")

        alias_target = aws_route53.RecordTarget.from_alias(
            alias_target=LoadBalancerTarget(self.app_service.load_balancer)
        )
        aws_route53.ARecord(self, f'{project}-private-record-set',
                            target=alias_target,
                            zone=private_hosted_zone,
                            record_name=stack_vars['ROUTE53_DOMAIN_RECORD']
                            )

        if stack_vars['AWS_ENV_CLASSIFICATION'] == "prod":
            self.app_scaling = self.app_service.service.auto_scale_task_count(
                min_capacity=int(stack_vars['MINIMUM_SCALE_CAPACITY']),
                max_capacity=int(stack_vars['MAXIMUM_SCALE_CAPACITY']))

            self.app_scaling.scale_on_cpu_utilization(
                f"{project}_app_CPU_Scaling",
                target_utilization_percent=70,
                scale_in_cooldown=core.Duration.seconds(60),
                scale_out_cooldown=core.Duration.seconds(60)
            )

            self.app_scaling.scale_on_memory_utilization(
                f"{project}_app_MEM_Scaling",
                target_utilization_percent=60,
                scale_in_cooldown=core.Duration.seconds(60),
                scale_out_cooldown=core.Duration.seconds(60)
            )

        self.app_service.target_group.configure_health_check(enabled=True,
                                                             healthy_http_codes="200",
                                                             healthy_threshold_count=5,
                                                             interval=core.Duration.seconds(
                                                                 30),
                                                             port="3000",
                                                             protocol=ApplicationProtocol.HTTP,
                                                             path="/ping/",
                                                             timeout=core.Duration.seconds(
                                                                 5),
                                                             unhealthy_threshold_count=2,
                                                             )

        self.app_service.target_group.set_attribute(
            "deregistration_delay.timeout_seconds", "30")

        console_task = ecs.FargateTaskDefinition(
            self, f"{project}-console-task", family=f"{project}-console-task", cpu=512,
            memory_limit_mib=1024)

        self.allow_ssm(console_task)
        self.allow_s3(console_task)
        self.allow_fargate_exec(console_task)

        console_task.add_container(f"{project}-console-task",
                                   image=ecs.ContainerImage.from_ecr_repository(ecr_repo),
                                   essential=True, environment=stack_vars,
                                   command=["sh", "-c", "while true; do continue; done"],
                                   logging=ecs.LogDrivers.aws_logs(stream_prefix='console', log_group=log_group_obj)
                                   )
        # Event rule stack
        EventRuleCloudStack(scope=self, id="ERStack", project=project, stack_vars=stack_vars,
                            pipeline_name=pipeline_name)

    def allow_fargate_exec(self, task):
        self.exec_command_policy_count += 1
        # Policy to enable Exec on Fargate containers
        task.task_role.add_managed_policy(
            ManagedPolicy.from_managed_policy_arn(self, f'ECSExecCommandPolicy{self.exec_command_policy_count}',
                                                  'arn:aws:iam::414325586463:policy/ECSExecCommandPolicy'))

    def allow_ssm(self, task):
        task.add_to_task_role_policy(
            PolicyStatement(
                actions=["ssm:GetParamaters"],
                effect=Effect.ALLOW,
                resources=['*']
            )
        )

    def allow_s3(self, task):
        if not self.stack_vars.get('S3_BUCKET', None):
            return
        task.add_to_task_role_policy(
            PolicyStatement(
                actions=[
                    "s3:ReplicateObject",
                    "s3:PutObject",
                    "s3:GetObjectAcl",
                    "s3:GetObject",
                    "s3:PutBucketLogging",
                    "s3:GetBucketCORS",
                    "s3:ListBucket",
                    "s3:PutBucketCORS",
                    "s3:DeleteObject",
                    "s3:GetBucketLocation",
                    "s3:GetBucketPolicy"
                ],
                effect=Effect.ALLOW,
                resources=[
                    f"arn:aws:s3:::{self.stack_vars['S3_BUCKET']}",
                    f"arn:aws:s3:::{self.stack_vars['S3_BUCKET']}/*"
                ]
            )
        )
