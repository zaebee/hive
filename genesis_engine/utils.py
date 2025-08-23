import os
from typing import Optional

def find_component_path(component_name: str, domain: Optional[str] = None) -> Optional[str]:
    """
    Finds the full path to a component directory by its name and optional domain.

    This function scans the 'hive/components' directory. If a domain is provided,
    it limits the search to that domain. If not, it searches all domains.

    :param component_name: The name of the component to find.
    :param domain: The domain to search in. If None, searches all domains.
    :return: The full path to the component directory, or None if not found.
    :raises: ValueError if the component name is not unique across the searched
             domains and no specific domain was provided.
    """
    base_dir = 'hive/components'
    if not os.path.isdir(base_dir):
        return None

    found_paths = []

    domains_to_search = [domain] if domain else os.listdir(base_dir)

    for domain_name in domains_to_search:
        # This check is important if os.listdir() is used, as it can include files.
        domain_path = os.path.join(base_dir, domain_name)
        if not os.path.isdir(domain_path):
            continue

        component_path = os.path.join(domain_path, component_name)
        metadata_path = os.path.join(component_path, '.genesis')

        # A valid component is a directory containing a .genesis file.
        if os.path.isdir(component_path) and os.path.isfile(metadata_path):
            found_paths.append(component_path)

    if len(found_paths) == 0:
        return None

    if len(found_paths) == 1:
        return found_paths[0]

    # If we get here, multiple components were found.
    raise ValueError(
        f"Multiple components named '{component_name}' found in different domains. "
        f"Please specify a domain using the --domain option."
    )
