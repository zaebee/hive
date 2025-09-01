from jinja2 import Environment, FileSystemLoader
import os

def generate_from_template(template_path: str, output_path: str, context: dict):
    """
    Generates a file from a Jinja2 template.
    """
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Set up the Jinja2 environment
    template_dir = os.path.dirname(template_path)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(os.path.basename(template_path))

    # Render the template
    output = template.render(context)

    # Write the output to the file
    with open(output_path, "w") as f:
        f.write(output)

    print(f"Generated {output_path}")
