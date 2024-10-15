import rich_click as click
import yaml
from llmscout.__about__ import __version__
from .scanner import do_scan_azure
from .litellm_patched import run_server as litellm_server, export as litellm_export

def llmscout():
    cli.add_command(litellm_server, "litellm")
    cli()

@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="llmscout")
def cli():
    pass

@cli.command()
@click.option('--out', '-o', default="scan.yaml", type=click.Path(), help="Output file.")
@click.option('--format', '-f', default="llmscout", type=str, help="Format of the output file.")
@click.option('--user-id', '-u', default=None, type=str, help="Restricts to resources for which user id has OpenAI User role.")
@click.option('--resource-group', '-g', default=None, type=str, help="Restricts to resources in resource group.")
def scan(out, format, user_id, resource_group):
    scanning = do_scan_azure(user_id, resource_group)

    click.echo(f"Writing scanning result to {out} in format {format}")
    if format == "litellm":
        litellm_export(scanning, out)
    else:
        with open(out, 'w') as f:
            yaml.dump(scanning, f)
