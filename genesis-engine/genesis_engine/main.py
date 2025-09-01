import typer
from typing_extensions import Annotated

app = typer.Typer()

def version_callback(value: bool):
    if value:
        print("Genesis Engine v0.1.0")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
):
    pass

generate_app = typer.Typer()
app.add_typer(generate_app, name="generate")

@generate_app.command("aggregate")
def generate_aggregate(
    name: str,
    commands: Annotated[str, typer.Option(help="Comma-separated list of commands.")] = "",
    events: Annotated[str, typer.Option(help="Comma-separated list of events.")] = "",
):
    """
    Generates a new aggregate.
    """
    from genesis_engine.core.generator import generate_from_template

    class_name = "".join(word.capitalize() for word in name.split("_"))
    template_path = "genesis_engine/templates/aggregate/aggregate.py.j2"
    output_path = f"aggregates/{name}_aggregate.py"

    context = {
        "aggregate_name": class_name,
        "commands": [c.strip() for c in commands.split(",")] if commands else [],
        "events": [e.strip() for e in events.split(",")] if events else [],
    }

    generate_from_template(template_path, output_path, context)

@generate_app.command("connector")
def generate_connector(
    name: str,
    type: Annotated[str, typer.Option(help="Type of connector (primary/secondary).")] = "primary",
    protocol: Annotated[str, typer.Option(help="Protocol used by the connector (e.g., http, db).")] = "http",
):
    """
    Generates a new connector.
    """
    from genesis_engine.core.generator import generate_from_template

    class_name = "".join(word.capitalize() for word in name.split("_"))
    template_path = "genesis_engine/templates/connector/connector.py.j2"
    output_path = f"connectors/{name}_connector.py"

    context = {
        "connector_name": class_name,
        "connector_type": type,
        "protocol": protocol,
    }

    generate_from_template(template_path, output_path, context)

@generate_app.command("transformation")
def generate_transformation(
    name: str,
):
    """
    Generates a new transformation.
    """
    from genesis_engine.core.generator import generate_from_template

    class_name = "".join(word.capitalize() for word in name.split("_"))
    template_path = "genesis_engine/templates/transformation/transformation.py.j2"
    output_path = f"transformations/{name}_transformation.py"

    context = {
        "transformation_name": class_name,
    }

    generate_from_template(template_path, output_path, context)

@app.command()
def validate():
    """
    Validates the project structure and architectural rules.
    """
    from genesis_engine.core.validator import validate_project_structure

    print("Running validation...")
    errors = validate_project_structure(".")
    if errors:
        print("Validation failed with the following errors:")
        for error in errors:
            print(f"- {error}")
        raise typer.Exit(code=1)
    else:
        print("Validation successful!")


analyze_app = typer.Typer()
app.add_typer(analyze_app, name="analyze")

@analyze_app.command("bonds")
def analyze_bonds_command():
    """
    Analyzes the 'chemical bonds' between components.
    """
    from genesis_engine.core.validator import analyze_bonds

    print("Analyzing bonds...")
    warnings = analyze_bonds(".")
    if warnings:
        print("Analysis found the following potential issues:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("No toxic bonds detected.")


if __name__ == "__main__":
    app()
