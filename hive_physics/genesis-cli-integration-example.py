import click
import os
import sys

# Add the repository root to the Python path to allow imports from hive_physics.
# This is for demonstration purposes. In a real scenario, hive-physics would be an installed package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hive_physics.measurements.temperature import measure_hive_temperature

# This file is a simulation of how the `genesis` CLI tool could be extended.
# Since the actual source code is in an external repository, this file
# demonstrates the proposed changes.

@click.group()
def cli():
    """
    The main entry point for the Genesis Engine CLI.
    A tool for scaffolding and managing Hive-based systems.
    """
    pass

# --- Existing Command Group (Placeholder) ---
@cli.group()
def hatch():
    """A placeholder for the existing 'hatch' command group."""
    pass

@hatch.command()
@click.argument('component_name')
def command(component_name: str):
    """A placeholder for the 'hatch command' subcommand."""
    click.echo(f"🥚 Mock: Hatching a new command component named '{component_name}'...")


# --- New 'measure' Command Group ---
@cli.group()
def measure():
    """Measures the physical constants of the Hive."""
    pass

@measure.command()
def temperature():
    """
    Measures the current thermodynamic temperature (T_hive) of the Hive.
    """
    click.echo("🌡️  Measuring Hive Temperature...")

    # In a real application, the path might be configured.
    # Here, we assume a relative path from the repo root.
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    if not os.path.exists(mock_file_path):
        click.secho(f"Error: Mock data file not found at '{mock_file_path}'.", fg='red')
        click.secho("Please run this command from the root of the repository.", fg='yellow')
        return

    try:
        t_hive = measure_hive_temperature(mock_file_path)

        if t_hive < 10:
            phase = "Hibernation"
            color = "blue"
        elif t_hive < 100:
            phase = "Stable"
            color = "green"
        elif t_hive < 1000:
            phase = "Overheated"
            color = "yellow"
        else:
            phase = "Meltdown"
            color = "red"

        click.echo("Measurement complete.")
        click.secho(f"  - Hive Temperature (T_hive): {t_hive:.4f}", bold=True)
        click.secho(f"  - Current Phase: {phase}", fg=color, bold=True)

    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg='red')


if __name__ == '__main__':
    # This makes the script runnable and allows testing the CLI structure.
    # Example usage from your terminal:
    # python hive_physics/genesis-cli-integration-example.py measure temperature
    cli()
