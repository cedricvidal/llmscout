import rich_click as click
import yaml
from llmscout.__about__ import __version__
from .scanner import do_scan_azure
from .litellm_patched import run_server as litellm_server

def llmscout():
    cli.add_command(litellm_server, "litellm")
    cli()

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="llmscout")
def cli():
    pass

@cli.command()
def scan():

    litellm_config = do_scan_azure()

    click.echo(f"Writing litellm_config.yaml")
    with open('litellm_config.yaml', 'w') as f:
        yaml.dump(litellm_config, f)
