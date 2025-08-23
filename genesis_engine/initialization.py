import os
import shutil
import jinja2

def initialize_project(project_name: str, template: str):
    """
    Initializes a new project directory from a template.

    :param project_name: The name of the new project (and its directory).
    :param template: The name of the project template to use.
    """
    # Define paths
    # Use __file__ to get a reliable path to the templates directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'project_templates', template)
    output_dir = project_name

    if not os.path.isdir(template_dir):
        print(f"Error: Template '{template}' not found at '{template_dir}'.")
        return

    if os.path.exists(output_dir):
        print(f"Error: Directory '{output_dir}' already exists.")
        return

    print(f"Creating project directory: {output_dir}")
    os.makedirs(output_dir)

    # Create context for Jinja2 rendering
    context = {
        'project_name': project_name,
    }

    # Set up Jinja2 environment to load templates from within the package
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath=template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Walk through the template directory and copy/render files
    for root, dirs, files in os.walk(template_dir):
        # Calculate the relative path from the template root to the current directory
        relative_dir = os.path.relpath(root, template_dir)

        # Create corresponding directories in the output path
        current_output_dir = os.path.join(output_dir, relative_dir) if relative_dir != '.' else output_dir
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir)

        for filename in files:
            # Path to the source template file
            template_file_path = os.path.join(root, filename)
            # Path to the destination file
            output_filepath = os.path.join(current_output_dir, filename.replace('.j2', ''))

            if filename.endswith('.j2'):
                # The template name for Jinja is relative to the loader's path
                template_name = os.path.relpath(template_file_path, template_dir)
                template_obj = env.get_template(template_name)
                rendered_content = template_obj.render(context)
                with open(output_filepath, 'w') as f:
                    f.write(rendered_content)
                print(f"  -> Rendered {filename} to {output_filepath}")
            else:
                # Just copy the file
                shutil.copy2(template_file_path, output_filepath)
                print(f"  -> Copied {filename} to {output_filepath}")

    print(f"\n✅ Project '{project_name}' initialized successfully.")
    print(f"To get started, run: cd {project_name}")
