import click
from .hatch import hatch_component
from .listing import list_components

@click.group()
def genesis():
    """
    The Genesis Engine is the instrument of creation within the Hive.

    It embodies the core principle that components are born, not built.
    """
    pass

@genesis.command('list')
@click.option('--type', 'component_type', default=None, help='Filter by component type.')
@click.option('--domain', default=None, help='Filter by domain.')
def list_cmd(component_type, domain):
    """Lists all components in the Hive."""
    list_components(component_type, domain)


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


@hatch.command("transformation")
@click.argument('component_name')
@click.option('--domain', required=True, help='The business domain for the component.')
def transformation(component_name, domain):
    """Hatches a new transformation component."""
    click.echo(f"Hatching transformation '{component_name}' in domain '{domain}'...")
    hatch_component('transformation', component_name, domain)
    click.echo(f"Successfully hatched transformation '{component_name}'.")


if __name__ == '__main__':
    genesis()
