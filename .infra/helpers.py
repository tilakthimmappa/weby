'''
function to get ENV VAR for pipeline and docker for test build
'''
import boto3
import copy


def ssm_parameter_value(ssm_instance, prefix, env_classification, value_object):
    ssm_value = None
    if value_object.get('ssm_key'):
        try:
            parameter = ssm_instance.get_parameter(Name=f"/{prefix}/{env_classification}/{value_object.get('ssm_key')}", WithDecryption=True)
            ssm_value = parameter['Parameter']['Value'].strip()
        except Exception as e:
            # TODO: call sentry
            pass

    return ssm_value


def get_ssm_values(prefix: str, env_classification: str, data: dict):
    ssm = boto3.client('ssm')
    stack_vars = dict()
    rspec_vars = dict()
    data = copy.deepcopy(data)
    worker_vars = data.pop('WORKER_ENVS', dict())
    for k, v in data.items():
        stack_vars[k] = v.get('{0}_default_value'.format(env_classification))
        ssm_value = ssm_parameter_value(ssm_instance=ssm, prefix=prefix, env_classification=env_classification, value_object=v)
        if ssm_value is not None:
            stack_vars[k] = ssm_value

        if v.get('is_docker_env'):
            rspec_vars[k] = stack_vars[k]

    # Worker envs values
    stack_vars['WORKER_ENVS'] = dict()
    for worker, worker_env in worker_vars.items():
        stack_vars['WORKER_ENVS'][worker] = dict()
        for worker_key, worker_value in worker_env.items():
            stack_vars['WORKER_ENVS'][worker][worker_key] = worker_value.get('{0}_default_value'.format(env_classification))
            ssm_value = ssm_parameter_value(ssm_instance=ssm, prefix=prefix, env_classification=env_classification, value_object=worker_value)
            if ssm_value is not None:
                stack_vars['WORKER_ENVS'][worker][worker_key] = ssm_value

    return stack_vars, rspec_vars
