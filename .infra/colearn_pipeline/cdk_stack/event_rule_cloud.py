from aws_cdk.core import Construct

from aws_cdk.aws_events import CfnRule


class EventRuleCloudStack:
    def __init__(self, *, scope: Construct, id: str, project: str, stack_vars: dict, pipeline_name: str, **kwargs):
        cloud_rule = CfnRule(scope, f'{stack_vars["AWS_ENV_CLASSIFICATION"]}-{project}-rule',
                        name=f'{stack_vars["AWS_ENV_CLASSIFICATION"]}-{project}-rule',
                        event_pattern={
                            "source": ["aws.codepipeline"],
                            "detail-type": ["CodePipeline Pipeline Execution State Change"],
                            "detail": {
                                "state": ["SUCCEEDED"],
                                "pipeline": [pipeline_name]
                            }
                        },
                        targets=[CfnRule.TargetProperty(arn=stack_vars['EVENT_RULE_LOG_ARN'], id='deployment-logs')]
                    )