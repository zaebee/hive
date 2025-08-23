import os
import json
import graphviz

def generate_graph(graph_type: str, output_filename: str):
    """
    Generates a graph of the Hive architecture.

    :param graph_type: The type of graph to generate (e.g., 'codons').
    :param output_filename: The base name for the output file.
    """
    if graph_type == 'codons':
        generate_codons_graph(output_filename)
    else:
        print(f"Error: Unknown graph type '{graph_type}'.")

def generate_codons_graph(output_filename: str):
    """
    Generates a graph where each component is a node, styled by its type (codon),
    and grouped by its domain.
    """
    base_dir = 'hive/components'
    if not os.path.isdir(base_dir):
        print("No 'hive/components' directory found. Nothing to graph.")
        return

    dot = graphviz.Digraph('HiveCodons', comment='Hive Component Codon Graph')
    dot.attr(rankdir='TB', size='12,12', splines='ortho')
    dot.attr('node', style='rounded,filled', fontname='Helvetica', fontsize='10')
    dot.attr('edge', arrowhead='none')

    # Define styles for different codon types
    styles = {
        'aggregate': {'shape': 'hexagon', 'fillcolor': '#A8DADC'}, # Light Blue
        'transformation': {'shape': 'ellipse', 'fillcolor': '#A8E6CF'}, # Light Green
        'default': {'shape': 'box', 'fillcolor': '#D3D3D3'}, # Grey
    }

    components_found = False
    for domain_name in sorted(os.listdir(base_dir)):
        domain_path = os.path.join(base_dir, domain_name)
        if not os.path.isdir(domain_path):
            continue

        # Create a subgraph for each domain for visual grouping
        with dot.subgraph(name=f'cluster_{domain_name}') as c:
            c.attr(label=domain_name, style='rounded', color='lightgrey')
            for component_name in sorted(os.listdir(domain_path)):
                component_path = os.path.join(domain_path, component_name)
                metadata_path = os.path.join(component_path, '.genesis')

                if os.path.isfile(metadata_path):
                    components_found = True
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)

                    codon_type = metadata.get('type', 'unknown')
                    style = styles.get(codon_type, styles['default'])

                    node_id = f"{domain_name}_{component_name}"
                    node_label = f"{component_name}\\n({codon_type})"
                    c.node(node_id, label=node_label, **style)

    if not components_found:
        print("No components found to graph.")
        return

    try:
        # Render the graph to a file (e.g., 'hive_graph.gv' and 'hive_graph.gv.svg')
        # The cleanup=True option removes the intermediate .gv source file.
        dot.render(output_filename, format='svg', view=False, cleanup=True)
        print(f"✅ Graph successfully generated: {output_filename}.svg")
    except graphviz.backend.ExecutableNotFound:
        print("\n❌ Error: `graphviz` executable not found in your system's PATH.")
        print("Please install the Graphviz software to generate graph visualizations.")
        print("  - On Debian/Ubuntu: `sudo apt-get install graphviz`")
        print("  - On macOS with Homebrew: `brew install graphviz`")
        print("  - On Windows with Chocolatey: `choco install graphviz`")
