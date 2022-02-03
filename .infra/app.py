#!/usr/bin/env python3

import os

from aws_cdk import core

from colearn_pipeline.pipeline_code import PipelineStack
from helpers import get_ssm_values
from stack_vars import (
    stack_envs,
    PROJECT,
    GIT_REPO,
    DEPLOYMENT_STAGE,
    ENV_CLASSIFICATION
)

# preset environment variables as a hash.
# Few will come from parameter store and a few others will come from secrets.

# CDK Docs here: https://docs.aws.amazon.com/cdk/api/latest/python/index.html
SSM_PREFIX = f'colearn/{PROJECT}'

app = core.App()
'''
Inputs:
VPC - Dictionary - VPC ID, AZs, Public Subnets, Private Subnets
Service Name - String - Name of Service
Task List - List of Dictionaries - Task Name, Task Configuration, Scaling Configuration
Domain - String - Domain Name to use for the service
'''
# dev stack
if DEPLOYMENT_STAGE['deploy_in_dev']:
    # dev stack ENV VAR

    dev_vars, dev_rspec_vars = get_ssm_values(
                                prefix=SSM_PREFIX,
                                env_classification=ENV_CLASSIFICATION['dev'],
                                data=stack_envs
                            )

    ## Dev env deployment
    dev_pipeline = PipelineStack(app,
                                f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['dev']}",
                                project=PROJECT,
                                git_repo=GIT_REPO,
                                stack_name=f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['dev']}",
                                stack_vars=dev_vars,
                                rspec_vars=dev_rspec_vars,
                                env=core.Environment(
                                    region=dev_vars['AWS_REGION'],
                                    account=dev_vars['ACCOUNT_ID']
                                )
                            )

# stage stack
if DEPLOYMENT_STAGE['deploy_in_stage']:
    # stage stack ENV VAR
    stage_vars, stage_rspec_vars = get_ssm_values(
                                prefix=SSM_PREFIX,
                                env_classification=ENV_CLASSIFICATION['stage'],
                                data=stack_envs
                            )
    ## Stage env deployment
    stage_pipeline = PipelineStack(app,
                                f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['stage']}",
                                project=PROJECT,
                                git_repo=GIT_REPO,
                                stack_name=f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['stage']}",
                                stack_vars=stage_vars,
                                rspec_vars=stage_rspec_vars,
                                env=core.Environment(
                                    region=stage_vars['AWS_REGION'],
                                    account=stage_vars['ACCOUNT_ID']
                                )
                            )

# prod stack
if DEPLOYMENT_STAGE['deploy_in_prod']:
    # prod stack ENV VAR
    prod_vars, prod_rspec_vars = get_ssm_values(
                                prefix=SSM_PREFIX,
                                env_classification=ENV_CLASSIFICATION['prod'],
                                data=stack_envs
                            )

    ## Prod env deployment
    prod_pipeline = PipelineStack(app,
                                f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['prod']}",
                                project=PROJECT,
                                git_repo=GIT_REPO,
                                stack_name=f"pipeline-{PROJECT}-{ENV_CLASSIFICATION['prod']}",
                                stack_vars=prod_vars,
                                rspec_vars=prod_rspec_vars,
                                env=core.Environment(
                                    region=prod_vars['AWS_REGION'],
                                    account=prod_vars['ACCOUNT_ID']
                                )
                            )

app.synth()
