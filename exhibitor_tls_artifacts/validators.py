import click
from pathlib import Path


def validate_dir_missing(ctx, param, value):
    """ click validator to ensure that artifacts directory does not exist """
    assert ctx or param  # For linting

    path = Path(value)

    if path.exists() or path.is_symlink():
        raise click.BadParameter(
            message="Artifacts location '{}' already exists.".format(value))

    return path
