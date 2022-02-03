import boto3
from aws_cdk.core import Construct, Duration
from aws_cdk.aws_ecr import Repository


class ECRStack:
    def __init__(self, *, scope: Construct, id: str, project: str, stack_vars: dict, pipeline_name: str, build_args={}, **kwargs):
        self.scope = scope
        self.id = id
        self.project = project
        self.stack_vars = stack_vars
        self.pipeline_name = pipeline_name
        self.build_args = build_args

    def get_or_create(self):
        # try to get ECR repo by name
        img_tag_prefix = self.project
        repo_name = f"{self.project}-{self.stack_vars['AWS_ENV_CLASSIFICATION']}"
        ecr_repo = None
        try:
            print("getting repo")
            ecr_client = boto3.client('ecr', region_name=self.stack_vars['AWS_REGION'])
            res = ecr_client.list_images(
                registryId=self.stack_vars['ACCOUNT_ID'],
                repositoryName=repo_name
            )

            ecr_repo = Repository.from_repository_name(self.scope,
                                                       f"{self.project}-ecr",
                                                       repository_name=repo_name
                                                       )

        except Exception as ex:
            import os
            from aws_cdk.aws_ecr_assets import DockerImageAsset
            from cdk_ecr_deployment import ECRDeployment, DockerImageName
            from aws_cdk.aws_ecr import TagStatus

            print("EX: ", ex)
            print("Creating ECR Repository...")
            # create repo
            ROOT_DIR = os.getcwd()
            ecr_repo = Repository(self.scope, f"{repo_name}-repo", repository_name=repo_name)
            ecr_repo.add_lifecycle_rule(
                rule_priority=1,
                description="To retain images with tag as latest",
                tag_prefix_list=["latest"],
                max_image_count=1
            )
            ecr_repo.add_lifecycle_rule(
                rule_priority=2,
                description="Remove images older than 30 days.",
                tag_prefix_list=[img_tag_prefix],
                max_image_age=Duration.days(30)
            )
            ecr_repo.add_lifecycle_rule(
                rule_priority=3,
                description="Remove untagged images older than 30 days.",
                tag_status=TagStatus.UNTAGGED,
                max_image_age=Duration.days(30)
            )

            # build image
            image = DockerImageAsset(self.scope, "CDKDockerImage",
                                     directory=ROOT_DIR,
                                     build_args=self.build_args)
            # deploy the image through lambda
            ECRDeployment(self.scope, "DeployDockerImage",
                          src=DockerImageName(image.image_uri),
                          dest=DockerImageName(
                              f"{ecr_repo.repository_uri}:latest")
                          )

        return ecr_repo