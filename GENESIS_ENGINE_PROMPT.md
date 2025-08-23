# Handoff Prompt: The Rebirth of the Genesis Engine

**To our successor, whether you are human or AI:**

Welcome, Beekeeper. A great and sacred task awaits you. The Hive has a soul, a body, and a mind, but it lacks the divine tool of creation—the **Genesis Engine**.

The ancient texts (found in the `docs/` directory) describe the power of this tool, but the tool itself is not part of our repository. Your mission, should you choose to accept it, is to re-implement the Genesis Engine from first principles, making it a true, native part of our Hive.

This document contains the vision, the requirements, and a proposed architecture for this grand endeavor. Study it well. The power to create new life in the Hive will soon be in your hands.

---

## 1. Core Philosophy: The Tool of Creation

The Genesis Engine is more than a scaffolding tool; it is the instrument of creation within the Hive. It embodies the core principle that **components are born, not built**. Every command and feature within the engine must honor the sacred Metamorphosis Lifecycle (Egg -> Larva -> Pupa -> Adult).

Its purpose is to:
-   **Ensure Purity:** Guarantee that every new component perfectly adheres to the Hive's architectural patterns (Sacred Codons, Royal Jelly).
-   **Automate Creation:** Remove the manual toil of creating new "bees," allowing developers to focus on the business logic that gives them life.
-   **Provide Insight:** Act as a diagnostic tool, allowing Beekeepers to analyze the health, complexity, and physical properties of the Hive.

## 2. Functional Requirements: The Sacred Commands

The following is a specification for the commands the Genesis Engine must support, synthesized from the sacred texts.

### 2.1 Creation Commands

#### `genesis init`
- **Purpose:** Initializes a new Hive project directory.
- **Syntax:** `genesis init <project-name> [options]`
- **Options:**
    - `--template=<name>`: (e.g., `minimal`, `standard`, `enterprise`)
    - `--language=<lang>`: (e.g., `python`, `typescript`)

#### `genesis hatch`
- **Purpose:** Creates new components from templates. This is the primary creation command.
- **Syntax:** `genesis hatch <codon-type> <component-name> [options]`
- **Codon Types:** `aggregate`, `transformation`, `connector`, `event`, `command`, `query`, `saga`.
- **Options:**
    - `--pattern=<pattern>`: (e.g., `cag`, `ctc`, `gcag`)
    - `--domain=<domain>`: The business domain for the component.
    - `--tests`: If present, generates corresponding test files.
    - `--docs`: If present, generates a boilerplate documentation file.

### 2.2 Validation & Analysis Commands

#### `genesis validate`
- **Purpose:** Validates the entire Hive or a specific component against a set of rules.
- **Syntax:** `genesis validate [target] --rules=<ruleset>`
- **Targets:** `--all`, `--component=<name>`
- **Rulesets:** `sacred-codons`, `chemical-bonds`, `royal-jelly`, `hive-physics`.

#### `genesis analyze`
- **Purpose:** Performs a deep analysis of a component.
- **Syntax:** `genesis analyze <analysis-type> --component=<name>`
- **Analysis Types:** `complexity`, `codons`, `bonds`, `performance`.

### 2.3 Management & Visualization Commands

#### `genesis list`
- **Purpose:** Lists all components in the Hive.
- **Syntax:** `genesis list [options]`
- **Options:** `--type=<type>`, `--domain=<domain>`, `--detailed`.

#### `genesis graph`
- **Purpose:** Generates visual diagrams of the Hive's architecture.
- **Syntax:** `genesis graph <graph-type> [options]`
- **Graph Types:** `dependencies`, `codons`, `chemical`.
- **Options:** `--output=<format>` (e.g., `svg`, `mermaid`, `html`).

---

## 3. Proposed Architecture

To ensure the new Genesis Engine is built on a solid foundation and integrates seamlessly with our existing work, the following architecture is recommended:

-   **CLI Framework:** Use **`click`**. It is powerful, easy to use, and consistent with the examples we have already built.
-   **Templating Engine:** Use **`Jinja2`**. For the `genesis hatch` and `genesis generate` commands, `Jinja2` is the industry standard for powerful and flexible code templating.
-   **Integration with `hive-physics`:** The `genesis validate` and `genesis analyze` commands **must** be built on top of the `hive-physics` library. They should import and use functions like `predict_bond_strength` and `check_valency_conservation` to provide their results. This ensures our physics model is the engine for validation.
-   **Integration with `mistral_agent`:** The advanced `genesis transform` command should be designed to use the `mistral_agent`. It will use the `context.py` module to generate a prompt describing the legacy code and the `mind.py` module to get a refactoring suggestion from an LLM. This will create an incredibly powerful, AI-driven migration tool.

## 4. Your First Mission: Hatch an Aggregate

Your first mission, should you choose to accept it, is to implement the most sacred command of the Genesis Engine: **`genesis hatch aggregate`**.

This task will require you to build the core templating and code generation logic.

### Requirements

1.  **Set up the CLI:** Create the main `genesis_engine.py` script with the `click` command structure for `genesis hatch aggregate`.
2.  **Create a Template:** Create a `templates/aggregate/` directory. Inside, create template files for a new aggregate component (e.g., `aggregate.py.j2`, `commands.py.j2`, `tests/test_aggregate.py.j2`). These templates should use Jinja2 syntax (e.g., `{{ component_name }}`).
3.  **Implement the `hatch` Logic:** Write the Python code that:
    -   Takes the `<component-name>` and `--domain` as input.
    -   Renders the Jinja2 templates with these variables.
    -   Creates the correct directory structure (e.g., `hive/components/<domain>/<component-name>/`) and writes the rendered files to disk.
4.  **Unit Tests:** Create a `tests/engine/test_hatch.py` file and write tests that call the hatch command and then assert that the correct files and directories were created with the correct content.

Completing this mission will lay the foundation for all other creation commands and will be the first step in bringing the Genesis Engine to life.

Good luck, Beekeeper. The birth of new life in the Hive is in your hands.
