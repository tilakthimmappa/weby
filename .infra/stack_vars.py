"""
list of env variables used for stack to map with value in ssm
initial key in dictionary is name of ENV VAR
"default_value": value in case you dont have key in ssm. default value can be used for test purpose as well.
"ssm_key": name of key placed in ssm
"is_docker_env": indicates wheather to include var in rspec/unit test stage of pipeline as docker env
"""
PROJECT = "weby-service"
GIT_REPO = "weby"

DEPLOYMENT_STAGE = {
    "deploy_in_dev": True,
    "deploy_in_stage": False,
    "deploy_in_prod": False,
}

ENV_CLASSIFICATION = {"dev": "dev", "stage": "stage", "prod": "prod"}

# Please do not modify unless you know what you are doing. Privilage is only provided to infra team to modify the changes for 'infra_envs'

infra_envs = {
    "ACCOUNT_ID": {
        "dev_default_value": "414325586463",
        "stage_default_value": "414325586463",
        "prod_default_value": "414325586463",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "ACM_CERTIFICATE": {
        "dev_default_value": "arn:aws:acm:ap-south-1:414325586463:certificate/6e3d0d5c-2316-4b05-913f-8ee295c27af0",
        "stage_default_value": "certi-here",
        "prod_default_value": "certi-here",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "AWS_REGION": {
        "dev_default_value": "ap-south-1",
        "stage_default_value": "ap-northeast-1",
        "prod_default_value": "ap-southeast-1",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "AWS_ENV_CLASSIFICATION": {
        "dev_default_value": ENV_CLASSIFICATION["dev"],
        "stage_default_value": ENV_CLASSIFICATION["stage"],
        "prod_default_value": ENV_CLASSIFICATION["prod"],
        "ssm_key": "",
        "is_docker_env": False,
    },
    "CLUSTER_NAME": {
        "dev_default_value": f"{ENV_CLASSIFICATION['dev']}-{PROJECT}",
        "stage_default_value": f"{ENV_CLASSIFICATION['stage']}-{PROJECT}",
        "prod_default_value": f"{ENV_CLASSIFICATION['prod']}-{PROJECT}",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "IS_DEFAULT_VPC": {
        "dev_default_value": "False",
        "stage_default_value": "False",
        "prod_default_value": "False",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "ROUTE53_DOMAIN_RECORD": {
        "dev_default_value": "weby-dev.colearn.id",
        "stage_default_value": "weby-stage.colearn.id",
        "prod_default_value": "weby.colearn.id",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "SENTRY_ENV": {
        "dev_default_value": "development",
        "stage_default_value": "staging",
        "prod_default_value": "production",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "SENTRY_DSN": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "sentry_dsn",
        "is_docker_env": False,
    },
    "VPC_ID": {
        "dev_default_value": "vpc-0d7807c5fb4fb14fb",
        "stage_default_value": "vpc-04ef202fb3d784d33",
        "prod_default_value": "vpc-0cdb299f20dae0eaf",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "AVAILABILITY_ZONES": {
        "dev_default_value": "ap-south-1b,ap-south-1a",
        "stage_default_value": "ap-northeast-1c,ap-northeast-1a",
        "prod_default_value": "ap-southeast-1b,ap-southeast-1a,ap-southeast-1c",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "PUBLIC_SUBNET_IDS": {
        "dev_default_value": "subnet-0cd450ad874d6126b,subnet-04c0245eaaffab26b",
        "stage_default_value": "subnet-08dc13e24223a642d,subnet-062bfda60698dda7e",
        "prod_default_value": "subnet-0e06661f52cbf8d73,subnet-070ca8ce6edb08a5a,subnet-03aa8565b87ca7091",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "PRIVATE_SUBNET_IDS": {
        "dev_default_value": "subnet-0784be1ffaf14ad16,subnet-01347888414ae1aea",
        "stage_default_value": "subnet-04fba3f42db2a1600,subnet-0e9cc0911a8b2dddc",
        "prod_default_value": "subnet-05dca7268a5f46f1f,subnet-07a4f57d01a3bb4bb,subnet-0fed6017cb0e95b96",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "LB_SECURITY_GROUP": {
        "dev_default_value": "sg-0df328e41df2f2569",
        "stage_default_value": "sg-02f6bd7de8bd3832b",
        "prod_default_value": "sg-02b623ab89e27a253",
        "ssm_key": "",
        "is_docker_env": False
    },
    "STORAGE_BUCKET": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "EVENT_RULE_LOG_ARN": {
        "dev_default_value": "arn:aws:logs:ap-south-1:414325586463:log-group:/aws/events/deployment-logs",
        "stage_default_value": "arn:aws:logs:ap-northeast-1:414325586463:log-group:/aws/events/deployment-logs",
        "prod_default_value": "arn:aws:logs:ap-southeast-1:414325586463:log-group:/aws/events/deployment-logs",
        "ssm_key": "",
        "is_docker_env": False,
    },
    # developers can modify the dev_default_value, stage_default_value as they prefer here for corresponding environment.
    "GIT_BRANCH": {
        "dev_default_value": "cdk",  # BRANCH TO DEPLOY UNDER DEVELOPMENT ENVIRONMENT
        "stage_default_value": "master",  # BRANCH TO DEPLOY UNDER STAGING ENVIRONMENT
        # Please do not modify the prod_default_value.
        "prod_default_value": "master",  # BRANCH TO DEPLOY UNDER PRODUCITON ENVIRONMENT.
        "ssm_key": "",
        "is_docker_env": False,
    },
    "MINIMUM_SCALE_CAPACITY": {
        "dev_default_value": "1",
        "stage_default_value": "1",
        "prod_default_value": "2",
        "ssm_key": "",
        "is_docker_env": False
    },
    "MAXIMUM_SCALE_CAPACITY": {
        "dev_default_value": "1",
        "stage_default_value": "1",
        "prod_default_value": "3",
        "ssm_key": "",
        "is_docker_env": False
    }
}

# environment variable related to application.
# developers are to modify the env values below except for prod_default_value (unless sure about it)
app_envs = {
    "STORAGE_ACCESS_KEY": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "STORAGE_ACCESS_SECRET": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "STORAGE_HOST": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "ELASTICSEARCH_URL": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    },
    "ELASTICSEARCH_PREFIX": {
        "dev_default_value": "",
        "stage_default_value": "",
        "prod_default_value": "",
        "ssm_key": "",
        "is_docker_env": False,
    }
}

stack_envs = {**infra_envs, **app_envs}

# envs for celery/sidekiq workers
worker_envs = {
}

stack_envs = {**stack_envs, **{"WORKER_ENVS": worker_envs}}
