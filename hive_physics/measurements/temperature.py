import json
from datetime import datetime

def measure_hive_temperature(metrics_file: str) -> float:
    """
    Measures the Hive's thermodynamic temperature (T_hive).

    T_hive is defined as the average event processing rate per component.
    Formula: T_hive = (Total Events / Second) / (Number of Components)

    This function reads a snapshot of hive metrics from a JSON file
    to perform the calculation.

    Args:
        metrics_file: The path to the JSON file containing mock metrics.

    Returns:
        The calculated T_hive value. Returns 0 if there are no events or components.
    """
    try:
        with open(metrics_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Metrics file not found at {metrics_file}")
        return 0.0
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {metrics_file}")
        return 0.0

    num_components = data.get("hive_snapshot", {}).get("total_components", 0)
    events = data.get("recent_events", [])

    if not events or num_components == 0:
        return 0.0

    # Parse timestamps and find the time window.
    # The 'Z' suffix indicates UTC, which fromisoformat can handle in Python 3.11+.
    # For broader compatibility, we manually replace 'Z' with '+00:00'.
    timestamps = [datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) for e in events]
    min_time = min(timestamps)
    max_time = max(timestamps)

    duration_seconds = (max_time - min_time).total_seconds()
    num_events = len(events)

    # If the duration is very short (or zero), we can't get a meaningful rate.
    # In a real system, you'd sample over a fixed window (e.g., 1 minute).
    # For this mock data, we'll assume a minimum 1-second window if duration is less.
    if duration_seconds < 1.0:
        duration_seconds = 1.0

    events_per_second = num_events / duration_seconds
    hive_temperature = events_per_second / num_components

    return hive_temperature

if __name__ == '__main__':
    # This allows the script to be run directly for testing.
    # It assumes the script is run from the root of the repository.
    mock_file_path = 'hive_physics/data/mock_metrics.json'

    print(f"--- Measuring Hive Temperature from mock data: {mock_file_path} ---")

    temperature = measure_hive_temperature(mock_file_path)

    print(f"\nCalculated Hive Temperature (T_hive): {temperature:.4f}")

    # Add interpretation based on the phases defined in the original document
    if temperature < 10:
        phase = "Hibernation"
    elif temperature < 100:
        phase = "Stable"
    elif temperature < 1000:
        phase = "Overheated"
    else:
        phase = "Meltdown"

    print(f"Hive Phase: {phase}")
