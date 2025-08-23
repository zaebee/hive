import os
import json
import jinja2

def to_pascal_case(s: str) -> str:
    """Converts a snake_case string to PascalCase."""
    return "".join(word.capitalize() for word in s.split('_'))

def hatch_component(component_type: str, component_name: str, domain: str):
    """
    Hatches a new component by rendering templates.

    :param component_type: The type of component to hatch (e.g., 'aggregate').
    :param component_name: The name of the new component (e.g., 'shopping_cart').
    :param domain: The business domain for the component (e.g., 'e_commerce').
    """
    # Define paths robustly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates', component_type)
    output_dir_base = os.path.join('hive', 'components', domain, component_name)

    if not os.path.isdir(template_dir):
        print(f"Error: Template type '{component_type}' not found.")
        return

    # Create context for Jinja2 rendering
    context = {
        'component_name': component_name,
        'component_name_pascal_case': to_pascal_case(component_name),
        'domain': domain,
    }

    # Set up Jinja2 environment with a reliable loader path
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Walk through the template directory
    for root, dirs, files in os.walk(template_dir):
        relative_dir = os.path.relpath(root, template_dir)

        current_output_dir = os.path.join(output_dir_base, relative_dir) if relative_dir != '.' else output_dir_base
        os.makedirs(current_output_dir, exist_ok=True)

        for filename in files:
            if filename.endswith('.j2'):
                # Template name for Jinja is relative to the loader's search path
                template_name = os.path.join(relative_dir, filename) if relative_dir != '.' else filename
                template = env.get_template(template_name)

                rendered_content = template.render(context)

                output_filename = filename[:-3]
                output_filepath = os.path.join(current_output_dir, output_filename)

                with open(output_filepath, 'w') as f:
                    f.write(rendered_content)
                print(f"Created file: {output_filepath}")

    # Create metadata file
    metadata = {
        'type': component_type,
        'name': component_name,
        'domain': domain,
    }
    metadata_filepath = os.path.join(output_dir_base, '.genesis')
    with open(metadata_filepath, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Created metadata file: {metadata_filepath}")
