import click
from pathlib import Path


def validate_dir_missing(ctx, param, value):
    """ click validator to ensure that artifacts directory does not exist """
    path = Path(value)

    if path.exists():
        raise click.BadParameter(message="Artifacts directory cannot exist!")

    return path
