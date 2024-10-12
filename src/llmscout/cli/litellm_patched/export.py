import click
import yaml

def export(scanning, filepath = 'litellm_config.yaml'):
    model_list = []
    litellm_config = {
        "model_list": model_list,
        "litellm_settings": {
            "enable_azure_ad_token_refresh": "true"
        }
    }
    for endpoint in scanning:
        model = endpoint['model']
        model_id = f"{model['name']}@{model['version']}"
        deployment_name = endpoint['deployment_name']
        api_base = endpoint['endpoint']
        tpm = int(endpoint['sku']['capacity']) * 1000
        model_list.append({
            "model_name": model_id,
            "litellm_params": {
                "model": f"azure/{deployment_name}",
                "api_base": api_base,
                "tpm": tpm,
                "tenant_id": "HACK"
            }
        })

    with open(filepath, 'w') as f:
        yaml.dump(litellm_config, f)
