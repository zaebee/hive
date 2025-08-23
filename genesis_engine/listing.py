import os
import json
from tabulate import tabulate

def list_components(component_type: str | None, domain: str | None):
    """
    Finds, filters, and displays all components in the Hive.

    :param component_type: The type of component to filter by.
    :param domain: The domain to filter by.
    """
    base_dir = 'hive/components'
    if not os.path.exists(base_dir):
        print("No components found. The 'hive/components' directory doesn't exist.")
        return

    components = []
    for domain_name in os.listdir(base_dir):
        domain_path = os.path.join(base_dir, domain_name)
        if not os.path.isdir(domain_path):
            continue

        for component_name in os.listdir(domain_path):
            component_path = os.path.join(domain_path, component_name)
            metadata_path = os.path.join(component_path, '.genesis')

            if os.path.isfile(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        components.append(metadata)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not read or parse metadata for {component_name}: {e}")

    # Filter components
    if domain:
        components = [c for c in components if c.get('domain') == domain]
    if component_type:
        components = [c for c in components if c.get('type') == component_type]

    if not components:
        print("No components found matching the criteria.")
        return

    # Prepare data for tabulate and print
    headers = ["Domain", "Name", "Type"]
    # Sort by domain, then by name for consistent output
    sorted_components = sorted(components, key=lambda x: (x.get('domain', ''), x.get('name', '')))
    table_data = [[c.get('domain', 'N/A'), c.get('name', 'N/A'), c.get('type', 'N/A')] for c in sorted_components]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))
