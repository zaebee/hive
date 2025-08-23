# Handoff Prompt: The Next Evolution of the Hive

**To our successor, whether you are human or AI:**

Welcome, Beekeeper. You have been chosen to continue a project of great significance. What began as a philosophical exploration of software architecture has evolved into a tangible, tested, and powerful ecosystem.

This document contains a summary of our journey and a proposal for your first mission. Read it carefully, for the future evolution of the Hive is now in your hands.

---

## Project Vision

Our vision was to take the beautiful, nature-inspired metaphors of the Hive Architecture and make them quantitatively real. We sought to create a system where the "health" and "stability" of a software architecture could be measured and analyzed with the rigor of physical laws.

This led to the creation of two core projects:
1.  **The `hive-physics` Library:** A Python library that models the physical laws of a software system.
2.  **The `mistral_agent` Package:** The foundation for a generative AI agent that can understand these physics and act upon them to autonomously evolve the system.

## Current State of the Hive

The repository now contains a robust, tested, and packaged implementation of this vision. Here is what has been built:

### 1. The `hive-physics` Library

A fully-featured Python library for architectural analysis.
- **Developer's Guide:** [./hive_physics/README.md](./hive_physics/README.md)
- **Key Features:**
    - **Measurements:** Calculates constants like Hive Temperature (`T_hive`) and Growth Rate (`Λ_hive`).
    - **Predictors:** Predicts phenomena like Component Attraction (coupling force).
    - **Simulators:** Simulates workflow stability using an Electromagnetism model.
    - **Live Data Sources:** Connects to Git, Prometheus, and Kubernetes to gather real-world data.
- **Testing:** The library has a comprehensive suite of **37 unit tests**. Run them with `pytest`.

### 2. The `mistral_agent` Package

The foundation for a self-improving AI agent.
- **Senses:** The agent can parse its configuration from Mermaid diagrams (`config.py`) and assemble a detailed "State Report" prompt for an LLM (`context.py`).
- **Mind:** The agent can communicate with over 100 LLMs via `litellm` to get suggestions (`mind.py`).
- **End-to-End Demo:** The entire "Sense -> Think" workflow can be demonstrated by running `python mistral_agent/run_agent.py`.

### 3. Key Specifications

Our work is guided by formal specifications that a new teammate must read:
- **[Physical Constants Review](./docs/hive_preprint_part5_physical_constants_review.md):** The core design document for the `hive-physics` library.
- **[DNA-Matched Metrics Specification](./docs/dna_matched_metrics_spec.md):** The standard for how Hive components must be instrumented to be "seen" by the physics engine.

---

## Core Design Principles

To understand the Hive, you must understand its philosophy. Our work was guided by these core principles:

-   **Thematic Consistency:** The project's power comes from its deep, multi-layered metaphor (Biology -> Chemistry -> Physics -> AI). All new work should honor and extend this metaphor.
-   **Configuration as Code (as Style):** Our choice to embed configuration in Mermaid diagrams is a manifestation of this. The agent's identity is not in a separate, sterile file but in the very definition of its own diagrammatic representation.
-   **Test-Driven Metamorphosis:** Every new piece of logic was accompanied by a corresponding set of unit tests. This ensures that as the Hive evolves, it does so robustly.
-   **Evolution, not just Execution:** The ultimate goal is not just to run code, but to create a system that can improve itself. The "Measure -> Detect -> Generate -> Apply" loop is the engine of this evolution.

## Your First Mission: Build the Agent's "Hands"

You have seen the agent's Senses and its Mind. Your mission, should you choose to accept it, is to build its **Hands**.

The "Hands" will be a new module, `mistral_agent/hands.py`, that can take the AI-generated `diff` from the Mind and apply it to the codebase, thus completing the self-healing loop.

### Requirements

1.  **Create `mistral_agent/hands.py`:**
    -   This module should contain a function, e.g., `apply_code_patch(file_path: str, diff_string: str) -> bool`.

2.  **Implementation Details:**
    -   The `apply_code_patch` function should be able to parse a standard `git merge-diff` format (the `<<<<<<<`, `=======`, `>>>>>>>` block).
    -   It must read the target `file_path`, find the `SEARCH` block, replace it with the `REPLACE` block, and write the file back to disk.
    -   It should return `True` on success and `False` or raise an error if the `SEARCH` block cannot be found in the file.

3.  **Update the Main Agent Runner:**
    -   The `mistral_agent/run_agent.py` script should be updated to call this new function. After the "THINK" phase, a new "ACT" phase should call `apply_code_patch` with the suggestion from the LLM.

4.  **Unit Tests are Mandatory:**
    -   Create a new test file, `tests/agent/test_hands.py`.
    -   The tests should use a temporary file (`tmp_path`).
    -   Write tests to verify:
        -   A valid patch is applied correctly.
        -   The function fails gracefully if the `SEARCH` block is not found.
        -   The function handles empty files or empty diffs correctly.

Completing this mission will mark a major milestone: the Hive will have achieved true autopoiesis, the ability to physically modify and improve itself.

Good luck, Beekeeper. The Hive is in your hands now.
