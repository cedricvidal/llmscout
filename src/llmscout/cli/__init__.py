import rich_click as click
import yaml
from dotenv import load_dotenv
from llmscout.__about__ import __version__
from .scanner import do_scan_azure, export_proxy_endpoints
from .azd_utils import load_azd_env
from .litellm_patched import run_server as litellm_server

def llmscout():
    cli.add_command(litellm_server, "litellm")
    cli()

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="llmscout")
def cli():
    pass

@cli.command()
@click.option('--scan-azure/--no-scan-azure', default=True, help='Whether to scan Azure searching for OpenAI endpoints.')
@click.option('--set-azd-env/--no-set-azd-env', default=True, help='Set the selected deployment names as azd environment variables.')
def scan(scan_azure, set_azd_env):

    if scan_azure:
        litellm_config = do_scan_azure()

        click.echo(f"Writing litellm_config.yaml")
        with open('litellm_config.yaml', 'w') as f:
            yaml.dump(litellm_config, f)

    if set_azd_env:
        load_azd_env()
        load_dotenv(".env")
        load_dotenv(".env.state")

        export_proxy_endpoints()
