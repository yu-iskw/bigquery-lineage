# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import click
import click_completion

from .data import data
from .completion import completion

# Initialize click-completion
click_completion.init()


@click.group()
@click.pass_context
def cli(context):
    """CLI body

    Args:
        context: click context
    """
    if context.invoked_subcommand is None:
        print(context.get_help())
    else:
        print('gonna invoke %s' % context.invoked_subcommand)


# Add sub commands
cli.add_command(data)
cli.add_command(completion)

