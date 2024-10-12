import subprocess
from itertools import groupby
import json
import click

def list_resource(resource_type):
    result = subprocess.run(['az', 'resource', 'list', '--out', 'json', '--resource-type', resource_type], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stderr)
    return json.loads(result.stdout)

def rest_call(method, url, version):
    result = subprocess.run(['az', 'rest', '--method', method, '--url', f"{url}?api-version={version}"], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stderr)
    return json.loads(result.stdout)

def list_cognitive_services_accounts():
    return list_resource("Microsoft.CognitiveServices/accounts")

def get_cognitive_services_account(resource_id):
    return rest_call("get", resource_id, "2023-05-01")

def get_deployments(resource_id):
    return rest_call("get", f"{resource_id}/deployments", "2023-05-01")['value']

def get_deployment_rate_limits(deployment):
    rates = {}
    deployment_properties = deployment['properties']
    if 'rateLimits' in deployment_properties:
        rateLimits = deployment_properties['rateLimits']
        rates = dict(groupby(rateLimits, lambda x: x['key']))
    return rates

def get_oai_endpoint(account):
    account_properties = account['properties']
    account_endpoints = account_properties['endpoints']
    return account_endpoints['OpenAI Language Model Instance API'] if 'OpenAI Language Model Instance API' in account_endpoints else None

def get_az_ad_signed_in_user():
    result = subprocess.run(['az', 'ad', 'signed-in-user', 'show', "--query", "id"], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def get_role_assignments(user_id, scope, role):
    result = subprocess.run([
        'az', 'role', 'assignment', 'list', 
        '--assignee', user_id, 
        '--out', 'json',
        '--scope', scope,
        '--include-inherited',
        '--role', role
        ], capture_output=True, text=True)
    if result.returncode:
        raise Exception("Failed to run command: " + result.stdout)
    return json.loads(result.stdout)

def has_role_assignment(user_id, scope, role):
    assignments = get_role_assignments(user_id, scope, role)
    return len(assignments) > 0

openai_user_role_id = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' # Cognitive Services OpenAI User

def bold(text):
    return click.style(text, bold=True)

def red(text):
    return click.style(text, bold=True, fg='red')

def green(text):
    return click.style(text, bold=True, fg='green')

def do_scan_azure():
    click.echo(f"Scanning Azure for OpenAI endpoints")
    accounts = list_cognitive_services_accounts()
    endpoints = []
    stats = {}
    signed_in_user_id = get_az_ad_signed_in_user()
    for account_digest in accounts:
        account_id = account_digest['id']
        resource_group = account_digest['resourceGroup']
        account_name = account_digest['name']
        granted = has_role_assignment(signed_in_user_id, account_id, openai_user_role_id)
        click.echo(f"Found OpenAI resource: {bold(account_name)} in {bold(resource_group)} - {green("GRANTED") if granted else red("DENIED")}")
        if granted:
            account = get_cognitive_services_account(account_id)
            oai_endpoint = get_oai_endpoint(account)
            deployments = get_deployments(account_id)
            for deployment in deployments:
                deployment_name = deployment['name']
                deployment_properties = deployment['properties']
                model = deployment_properties['model']
                model_name = model['name']
                model_version = model['version']
                model_id = f"{model_name}@{model_version}"
                rateLimits = get_deployment_rate_limits(deployment)
                sku = deployment['sku']
                sku_capacity = sku['capacity']
                sku_name = sku['name']

    #            if model_name in model_names:
                if not model_id in stats.keys():
                    stats[model_id] = {
                        "total_capacity": 0,
                        "total_endpoints": 0
                    }
                endpoints.append({
                    "deployment_name": deployment_name,
                    "endpoint": oai_endpoint,
                    "sku": {
                        "capacity": sku_capacity,
                        "name": sku_name
                    },
                    "model": {
                        "name": model_name,
                        "version": model_version
                    }
                })
                stats[model_id]['total_capacity'] += sku_capacity
                stats[model_id]['total_endpoints'] += 1
                click.echo(f" - Adding OpenAI endpoint: {bold(model_id)} ({sku_capacity} {sku_name})")

    click.echo("Total capacity by model:")
    for model_id, stat in stats.items():
        click.echo(f" - {model_id}: {stat['total_capacity']}")

    return endpoints
