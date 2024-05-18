import click
from nandita_config_parser import parse_config
from nandita_aws_manager import apply_configuration

@click.group()
def cli():
    """A simple CLI for managing AWS resources via IaC."""
    pass

@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
def apply(config_file):
    """Apply configurations from a JSON file."""
    config = parse_config(config_file)
    apply_configuration(config)

if __name__ == '__main__':
    cli()