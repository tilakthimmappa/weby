from aws_cdk import (
    core,
    aws_ecr,
    aws_codepipeline as codepipeline, pipelines,
)
from aws_cdk.aws_codebuild import LinuxBuildImage, PipelineProject, BuildEnvironment, BuildSpec
from aws_cdk.aws_codepipeline_actions import GitHubSourceAction, GitHubTrigger, CodeBuildAction, EcsDeployAction
from aws_cdk.aws_iam import ManagedPolicy, PolicyStatement, Effect
from aws_cdk.core import SecretValue, Duration
from aws_cdk.pipelines import CdkPipeline
from aws_cdk.aws_codepipeline import ArtifactPath

from .fargate_stack import FargateStack


class PipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, *, project: str, git_repo: str, stack_vars: dict,
                 rspec_vars: dict, branch="", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # Add Source stage
        branch = branch if branch else stack_vars.get('GIT_BRANCH', '')
        pipeline_name = f"{project}-cdk-pipeline"
        cdk_pipeline = CdkPipeline(self, f"{project}-cdk-pipeline",
                                   cloud_assembly_artifact=cloud_assembly_artifact,
                                   pipeline_name=pipeline_name,
                                   source_action=GitHubSourceAction(action_name="GitHub",
                                                                    branch=branch,
                                                                    output=source_artifact,
                                                                    owner="colearnhq",
                                                                    oauth_token=SecretValue.secrets_manager(
                                                                        "colearnhq-githubtoken"),
                                                                    repo=git_repo,
                                                                    trigger=GitHubTrigger.WEBHOOK),

                                   synth_action=pipelines.SimpleSynthAction(
                                       source_artifact=source_artifact,
                                       cloud_assembly_artifact=cloud_assembly_artifact,
                                       install_command="npm install -g aws-cdk@1.138.2 && pwd",
                                       build_command="python -m pip install -r .infra/requirements.txt",
                                       synth_command="cdk synth",
                                       role_policy_statements=[
                                           PolicyStatement(
                                               actions=[
                                                   "ssm:GetParameter",
                                                   "ecr:ListImages"
                                               ],
                                               resources=["*"]
                                           )
                                       ],
                                       environment={
                                           'privileged': True,
                                           'build_image': LinuxBuildImage.STANDARD_5_0},
                                   )
                                   )

        SIDEKIQ_KEY = stack_vars.get('SIDEKIQ_KEY')
        RAILS_ENV = stack_vars.get('RAILS_ENV')

        # run test cases
        # build docker image
        ecr_repo = aws_ecr.Repository.from_repository_name(self, f"{project}",
                                                           f"{project}-{stack_vars['AWS_ENV_CLASSIFICATION']}")

        # Docker / RSpec Test stage
        test_args = ' '.join([f'-e {key}={value}' for key, value in rspec_vars.items()])

        rspec_test_commands = [
            f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {ecr_repo.repository_uri}",
            f"SIDEKIQ_KEY={SIDEKIQ_KEY} REGION={self.region} docker-compose up -d --build",
            f"SIDEKIQ_KEY={SIDEKIQ_KEY} REGION={self.region} docker-compose run -e RAILS_ENV=test {test_args} rails_app bundle exec rails db:prepare",
            f"SIDEKIQ_KEY={SIDEKIQ_KEY} REGION={self.region} docker-compose run -e RAILS_ENV=test {test_args} rails_app bundle exec rspec",
            f"SIDEKIQ_KEY={SIDEKIQ_KEY} docker-compose down"
        ]

        rspec_test_proj = PipelineProject(
            self, f"{project}-rspec-test-project",
            project_name=f"{project}-rspec-test-project",
            environment=BuildEnvironment(
                build_image=LinuxBuildImage.STANDARD_5_0,
                privileged=True
            ),
            timeout=Duration.minutes(10),
            build_spec=BuildSpec.from_object({
                "version": "0.2",
                "run-as": "root",
                "phases": {
                    "build": {
                        "commands": rspec_test_commands
                    }
                },
                "artifacts": {
                },
            })
        )
        rspec_test_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPowerUser")
        )
        rspec_test_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess")
        )
        rspec_test_proj.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW, actions=["ssm:GetParameters"],
                                                           resources=["*"]))
        rspec_test_proj.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW, actions=["iam:*"],
                                                           resources=["*"]))
        rspec_test_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
        )
        rspec_test_action = CodeBuildAction(
            action_name=f"{project}-rspec-test",
            project=rspec_test_proj,
            input=source_artifact,
            outputs=[]
        )

        cdk_pipeline.code_pipeline.add_stage(stage_name="Rspec_Tests", actions=[rspec_test_action])

        docker_build_output = codepipeline.Artifact("DockerBuildOutput")
        build_commands = [
            f"export DOCKER_TAG={project}-$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c -8)",
            "echo $DOCKER_TAG",
            f"export DOCKER_IMG={ecr_repo.repository_uri}:$DOCKER_TAG",
            f"export DOCKER_LATEST={ecr_repo.repository_uri}:latest",
            f"export PROJECT={project}",
            "echo $DOCKER_LATEST",
            "echo $DOCKER_IMG",
            f"aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {ecr_repo.repository_uri}",
            f"docker build . --build-arg REGION={self.region} --build-arg SIDEKIQ_ENT_KEY='{SIDEKIQ_KEY}' --build-arg RAILS_ENV='{RAILS_ENV}' -t $DOCKER_IMG -t $DOCKER_LATEST",
            "docker push $DOCKER_IMG", "docker push $DOCKER_LATEST",
            'echo \'[{"name": "\'$PROJECT\'-app", "imageUri":"\'$DOCKER_LATEST\'"}]\' > app_imagedefinitions.json',
            'echo \'[{"name": "\'$PROJECT\'-sidekiq", "imageUri":"\'$DOCKER_LATEST\'"}]\' > '
            'sidekiq_imagedefinitions.json',
            'echo \'[{"name": "\'$PROJECT\'-console-task", "imageUri":"\'$DOCKER_LATEST\'"}]\' > '
            'console_imagedefinitions.json']

        build_proj = PipelineProject(
            self, f"{project}-build-project",
            project_name=f"{project}-build-project",
            environment=BuildEnvironment(
                build_image=LinuxBuildImage.STANDARD_5_0,
                privileged=True
            ),
            timeout=Duration.minutes(10),
            build_spec=BuildSpec.from_object({
                "version": "0.2",
                "run-as": "root",
                "phases": {
                    "build": {
                        "commands": build_commands
                    }
                },
                "artifacts": {
                    "files": [
                        "app_imagedefinitions.json",
                        "sidekiq_imagedefinitions.json",
                        "console_imagedefinitions.json"
                    ]
                },
            })
        )
        build_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryPowerUser")
        )
        build_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("IAMFullAccess")
        )
        build_proj.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW, actions=["ssm:GetParameters"],
                                                      resources=["*"]))
        build_proj.add_to_role_policy(PolicyStatement(effect=Effect.ALLOW, actions=["iam:*"],
                                                      resources=["*"]))
        build_proj.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
        )
        build_action = CodeBuildAction(
            action_name=f"{project}-build",
            project=build_proj,
            input=source_artifact,
            outputs=[docker_build_output]
        )

        cdk_pipeline.code_pipeline.add_stage(stage_name="Docker_Build", actions=[build_action])

        # deploy
        fargate_stack = FargateStack(self,
                                     f"0fargate",
                                     project=project,
                                     stack_vars=stack_vars,
                                     pipeline_name=pipeline_name,
                                     env=core.Environment(
                                         region=stack_vars['AWS_REGION'],
                                         account=stack_vars['ACCOUNT_ID']
                                     )
                                     )
        rails_service = EcsDeployAction(service=fargate_stack.app_service.service,
                                        deployment_timeout=core.Duration.minutes(5),
                                        image_file=ArtifactPath(
                                            artifact=docker_build_output,
                                            file_name="app_imagedefinitions.json"
                                        ),
                                        action_name=f"Deploy-{project}-app"
                                        )

        deploy_stage = cdk_pipeline.add_stage(stage_name="Deploy_To_Fargate")

        deploy_stage.add_actions(rails_service)
