# SPDX-FileCopyrightText: 2024-present Cedric Vidal <cedric@vidal.biz>
#
# SPDX-License-Identifier: MIT
import click

from llmscout.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="llmscout")
def llmscout():
    click.echo("Hello world!")
