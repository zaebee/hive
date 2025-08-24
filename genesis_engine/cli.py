import click
from .hatch import hatch_component
from .listing import list_components
from .validation import validate_component
from .analysis import analyze_component
from .initialization import initialize_project
from .graphing import generate_graph
from .refactoring import transform_component

@click.group()
def genesis():
    """
    The Genesis Engine is the instrument of creation within the Hive.

    It embodies the core principle that components are born, not built.
    """
    pass


@genesis.command('init')
@click.argument('project_name')
@click.option('--template', default='standard', help='The project template to use.')
def init_cmd(project_name, template):
    """Initializes a new Hive project."""
    click.echo(f"Initializing new Hive project '{project_name}' using template '{template}'...")
    initialize_project(project_name, template)


@genesis.command('list')
@click.option('--type', 'component_type', default=None, help='Filter by component type.')
@click.option('--domain', default=None, help='Filter by domain.')
def list_cmd(component_type, domain):
    """Lists all components in the Hive."""
    list_components(component_type, domain)


@genesis.command('validate')
@click.argument('target', type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.option('--rules', default='valency', help='The ruleset to apply (default: valency).')
def validate_cmd(target, rules):
    """Validates a component against a set of Hive Physics rules."""
    click.echo(f"Validating component at '{target}' using ruleset '{rules}'...")
    validate_component(target, rules)


@genesis.command('analyze')
@click.argument('analysis_type', type=click.Choice(['bonds'], case_sensitive=False))
@click.option('--component', 'component_name', required=True, help='The name of the component to analyze.')
@click.option('--domain', default=None, help='The domain of the component (required if name is not unique).')
def analyze_cmd(analysis_type, component_name, domain):
    """Performs a deep analysis of a component using Hive Physics."""
    click.echo(f"Analyzing '{analysis_type}' for component '{component_name}'...")
    analyze_component(analysis_type, component_name, domain)


@genesis.command('graph')
@click.argument('graph_type', type=click.Choice(['codons'], case_sensitive=False))
@click.option('--output', default='hive_graph', help='The base name for the output file (e.g., hive_graph.svg).')
def graph_cmd(graph_type, output):
    """Generates a visual diagram of the Hive's architecture."""
    click.echo(f"Generating '{graph_type}' graph...")
    generate_graph(graph_type, output)


@genesis.command('transform')
@click.argument('target_file', type=click.Path(exists=True, dir_okay=False, readable=True))
def transform_cmd(target_file):
    """Refactors a source code file using an AI agent."""
    click.echo(f"Initiating AI-powered transformation for '{target_file}'...")
    transform_component(target_file)


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
