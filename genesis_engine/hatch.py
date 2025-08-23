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
    # Define paths
    template_dir = os.path.join('genesis_engine', 'templates', component_type)
    output_dir_base = os.path.join('hive', 'components', domain, component_name)

    # Create context for Jinja2 rendering
    context = {
        'component_name': component_name,
        'component_name_pascal_case': to_pascal_case(component_name),
        'domain': domain,
    }

    # Set up Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath='.'),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Walk through the template directory
    for root, dirs, files in os.walk(template_dir):
        # Determine the relative path from the template directory
        relative_dir = os.path.relpath(root, template_dir)

        # Create corresponding directories in the output path
        current_output_dir = os.path.join(output_dir_base, relative_dir) if relative_dir != '.' else output_dir_base
        os.makedirs(current_output_dir, exist_ok=True)

        for filename in files:
            if filename.endswith('.j2'):
                template_file = os.path.join(root, filename)
                template = env.get_template(template_file)

                # Render the template
                rendered_content = template.render(context)

                # Write the rendered file to the output directory
                output_filename = filename[:-3]  # Remove the .j2 extension
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
