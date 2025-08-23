import click
from .hatch import hatch_component

@click.group()
def genesis():
    """
    The Genesis Engine is the instrument of creation within the Hive.

    It embodies the core principle that components are born, not built.
    """
    pass

@genesis.group()
def hatch():
    """Hatches new components from templates."""
    pass


@hatch.command("aggregate")
@click.argument('component_name')
@click.option('--domain', required=True, help='The business domain for the component.')
def aggregate(component_name, domain):
    """Hatches a new aggregate component."""
    click.echo(f"Hatching aggregate '{component_name}' in domain '{domain}'...")
    hatch_component('aggregate', component_name, domain)
    click.echo(f"Successfully hatched aggregate '{component_name}'.")


if __name__ == '__main__':
    genesis()
