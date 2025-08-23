import click
import os
import sys
import json
from pathlib import Path

# Since the hive_physics package is now installed in editable mode,
# we can import from it directly without modifying the path.
from hive_physics.measurements.temperature import measure_hive_temperature
from hive_physics.measurements.growth_rate import measure_growth_rate
from hive_physics.predictors.coupling import predict_bond_strength_for_pair as predict_bond_strength
from hive_physics.validation.rules import check_valency_conservation
from hive_physics.simulators.electromagnetism import find_most_stable_path
from hive_physics.adaptation.aggregate import AdaptationAggregate, ApplyPatchCommand

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


# --- New 'evolve' Command Group ---
@cli.group()
def evolve():
    """Evolves the Hive using the Adaptation Engine."""
    pass

@evolve.command('patch')
@click.option('--file', 'patch_file', required=True, type=click.Path(exists=True), help='Path to the patch file.')
def patch(patch_file):
    """Applies a patch to the Hive and measures its impact."""
    click.echo(f"🧬 Evolving the Hive with patch: {patch_file}")

    try:
        patch_content = Path(patch_file).read_text()

        aggregate = AdaptationAggregate("cli_aggregate")
        command = ApplyPatchCommand(patch=patch_content)

        events = aggregate._execute_immune_logic(command)

        # Display the results from the event
        result_event = events[0]
        status = result_event.payload.get("status", "unknown")
        pre_toxicity = result_event.payload.get("pre_toxicity", 0)
        post_toxicity = result_event.payload.get("post_toxicity", 0)

        click.echo("\n--- Evolution Result ---")
        if status == "applied":
            click.secho(f"✅ Patch successfully applied.", fg='green')
        else:
            click.secho(f"❌ Patch rejected.", fg='red')

        click.echo(f"  - Pre-patch Toxicity: {pre_toxicity:.2f}")
        click.echo(f"  - Post-patch Toxicity: {post_toxicity:.2f}")

        if post_toxicity < pre_toxicity:
            click.secho("  - Interpretation: This is a 'honey' patch, improving the Hive's health.", fg='cyan')
        elif post_toxicity > pre_toxicity:
            click.secho("  - Interpretation: This is a 'poison' patch, harming the Hive's health.", fg='yellow')
        else:
            click.secho("  - Interpretation: This patch is neutral.", fg='blue')

    except Exception as e:
        click.secho(f"An unexpected error occurred during evolution: {e}", fg='red')


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


@measure.command('growth-rate')
@click.option('--days', default=7, help='The number of days in the past to measure against.')
def growth_rate(days):
    """
    Measures the Hive Growth Rate (Λ_hive) over a given period.
    """
    click.echo(f"📈 Measuring Hive Growth Rate over the last {days} days...")

    try:
        lambda_hive = measure_growth_rate('.', days) # Use current directory for repo path

        click.echo("Measurement complete.")
        click.secho(f"  - Hive Growth Rate (Λ_hive): {lambda_hive:.4f} components/day", bold=True)

        if lambda_hive > 0.1:
            interpretation = "The Hive is in a period of rapid growth."
            color = "yellow"
        elif lambda_hive > 0:
            interpretation = "The Hive is growing slowly and steadily."
            color = "green"
        elif lambda_hive == 0:
            interpretation = "The Hive is stable."
            color = "blue"
        else:
            interpretation = "The Hive is shrinking (refactoring or decommissioning)."
            color = "red"

        click.secho(f"  - Interpretation: {interpretation}", fg=color)

    except Exception as e:
        click.secho(f"An error occurred: {e}", fg='red')


# --- New 'predict' Command Group ---
@cli.group()
def predict():
    """Predicts physical phenomena in the Hive."""
    pass

@predict.command('bond-strength')
@click.option('--c1', required=True, help='The ID of the first component.')
@click.option('--c2', required=True, help='The ID of the second component.')
def bond_strength(c1, c2):
    """
    Predicts the bond strength (gravitational force) between two components.
    """
    click.echo(f"🛰️  Predicting bond strength between '{c1}' and '{c2}'...")
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    if not os.path.exists(mock_file_path):
        click.secho(f"Error: Mock data file not found at '{mock_file_path}'.", fg='red')
        return

    try:
        strength = predict_bond_strength(mock_file_path, c1, c2)
        click.echo("Prediction complete.")
        click.secho(f"  - Predicted Force (F): {strength:.4f}", bold=True)

        if strength == float('inf'):
            click.secho("  - Interpretation: The components are at the same position (singularity). Infinite coupling.", fg='red')
        elif strength > 100:
            click.secho("  - Interpretation: A very strong bond. These components are tightly coupled.", fg='yellow')
        elif strength < 1:
            click.secho("  - Interpretation: A weak bond. These components are loosely coupled.", fg='green')
        else:
            click.secho("  - Interpretation: A moderate bond.", fg='blue')

    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg='red')


# --- New 'validate' Command Group ---
@cli.group()
def validate():
    """Validates the Hive against architectural and physical laws."""
    pass

@validate.command('physics')
@click.option('--strict', is_flag=True, help='Exit with an error code if validation fails.')
def physics(strict):
    """
    Validates the Hive against physical laws like Valency Conservation.
    """
    click.echo("⚖️  Validating Hive against physical laws...")
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    if not os.path.exists(mock_file_path):
        click.secho(f"Error: Mock data file not found at '{mock_file_path}'.", fg='red')
        if strict:
            sys.exit(1)
        return

    try:
        with open(mock_file_path, 'r') as f:
            data = json.load(f)

        workflows = data.get("sample_workflows", {})
        if not workflows:
            click.secho("No workflows found in mock data to validate.", fg='yellow')
            return

        click.echo(f"Found {len(workflows)} workflows to validate.")
        all_passed = True

        for wf_name in workflows:
            conserved, total_in, total_out = check_valency_conservation(mock_file_path, wf_name)
            if conserved:
                message = f"✅ PASSED: Workflow '{wf_name}' conserves valency ({total_in} -> {total_out})."
                click.secho(message, fg='green')
            else:
                message = f"❌ FAILED: Workflow '{wf_name}' violates Valency Conservation ({total_in} -> {total_out})."
                click.secho(message, fg='red', bold=True)
                all_passed = False

        click.echo("-" * 20)
        if all_passed:
            click.secho("🎉 All physics validations passed!", bold=True, fg='green')
        else:
            click.secho("🔥 Some physics validations failed.", bold=True, fg='red')
            if strict:
                click.secho("Exiting with error code due to --strict flag.", fg='red')
                sys.exit(1)

    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg='red')
        if strict:
            sys.exit(1)


# --- New 'simulate' Command Group ---
@cli.group()
def simulate():
    """Runs simulations based on Hive's physical laws."""
    pass

@simulate.command('workflow')
@click.option('--start-component', required=True, help='The ID of the component to start the simulation from.')
def workflow(start_component):
    """
    Simulates a stable workflow path using the Electromagnetism model.
    """
    click.echo(f"⚡ Simulating stable workflow starting from '{start_component}'...")
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    if not os.path.exists(mock_file_path):
        click.secho(f"Error: Mock data file not found at '{mock_file_path}'.", fg='red')
        return

    try:
        stable_path = find_most_stable_path(mock_file_path, start_component)

        path_str = " -> ".join(stable_path)
        click.echo("Simulation complete.")
        click.secho(f"  - Discovered Stable Path: {path_str}", bold=True)
        click.secho("  - Interpretation: This path represents the most energetically favorable workflow based on component charges and architectural distance.", fg='cyan')

    except ValueError as ve:
        click.secho(f"Input Error: {ve}", fg='red')
    except Exception as e:
        click.secho(f"An unexpected error occurred during simulation: {e}", fg='red')


if __name__ == '__main__':
    # This makes the script runnable and allows testing the CLI structure.
    # Example usage from your terminal:
    # python hive_physics/genesis-cli-integration-example.py simulate workflow --start-component comp_001
    cli()
