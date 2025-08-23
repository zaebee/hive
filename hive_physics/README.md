# The Hive Physics Library

Welcome to the Hive Physics Library (`hive-physics`), a tool for modeling, measuring, and simulating the physical laws of a Hive-based software architecture.

## 1. Overview

This library provides a unique approach to software analysis by applying concepts from classical and modern physics to a running system. By treating your software components as physical objects with properties like "mass," "charge," and "gravity," you can gain deep insights into your system's stability, coupling, and evolution.

This library is the reference implementation for the concepts outlined in the "Hive's Physical Constants" and "DNA-Matched Metrics" specifications.

## 2. Core Concepts

- **Physical Constants:** Your Hive is governed by a set of immutable constants (`G_hive`, `k_hive`, etc.) that define its behavior.
- **DNA-Matched Metrics:** To measure the physics, your application's components must emit a standard set of metrics based on their primitive type (their "DNA"). See the [DNA-Matched Metrics Specification](../docs/dna_matched_metrics_spec.md) for details.
- **Data Sources:** The library uses pluggable data sources to connect to real-world systems like Git, Prometheus, and Kubernetes to gather the data needed for its calculations.

## 3. Installation

The library can be installed directly from the repository using `pip`.

### Base Installation
```bash
# Install the core library and its direct dependencies
pip install -e .
```

### Installation with Optional Extras

To use the live data sources, you need to install the corresponding optional dependencies.

**For Prometheus Integration:**
```bash
pip install -e .[prometheus]
```

**For Kubernetes Integration:**
```bash
pip install -e .[kubernetes]
```

**To install all extras:**
```bash
pip install -e .[prometheus,kubernetes]
```
*Note: `GitPython` is included as a core dependency.*

## 4. Usage & Examples

Here are some examples of how to use the library's core features.

### Example 1: Measuring the Hive's Growth Rate

This uses the `GitDataSource` to analyze the repository's history.

```python
from hive_physics.measurements.growth_rate import measure_growth_rate

# Analyze the current repository over the last 30 days
lambda_hive = measure_growth_rate('.', days_ago=30)

print(f"Hive Growth Rate (Λ_hive): {lambda_hive:.4f} components/day")
```

### Example 2: Predicting Bond Strength Between Components

This example uses both Prometheus (for component mass) and Kubernetes (for the architectural graph) to predict the coupling force between two services.

```python
from hive_physics.datasources import PrometheusDataSource, KubernetesDataSource
from hive_physics.predictors.coupling import predict_bond_strength

# Initialize data sources
# Assumes PROMETHEUS_URL is set as an environment variable
prom_ds = PrometheusDataSource(api_url="http://localhost:9090")
# Assumes a valid kubeconfig or in-cluster service account
k8s_ds = KubernetesDataSource()

# Predict the bond strength for all connected components
bond_strengths = predict_bond_strength(prom_ds, k8s_ds)

print("--- Bond Strength Report ---")
for pair, force in bond_strengths.items():
    print(f"  - {pair}: {force:.4f}")
```

### Example 3: Simulating a Stable Workflow

This example uses the Electromagnetism model to discover the most stable workflow (chain of primitives) starting from a given component.

```python
from hive_physics.datasources import PrometheusDataSource, KubernetesDataSource
from hive_physics.simulators.electromagnetism import find_most_stable_path

# Initialize data sources
prom_ds = PrometheusDataSource(api_url="http://localhost:9090")
k8s_ds = KubernetesDataSource()

# Find the most stable path starting from the 'rest-connector' service
# This requires 'rest-connector' to be a service discoverable by the K8s data source.
stable_path = find_most_stable_path(prom_ds, k8s_ds, "rest-connector")

print("--- Discovered Stable Workflow ---")
print(" -> ".join(stable_path))
```

## 5. Instrumenting Your Application

For the live data sources to work, your Hive application must be instrumented to emit the standard "DNA-Matched Metrics."

Please see the full **[DNA-Matched Metrics Specification](../docs/dna_matched_metrics_spec.md)** for detailed guidance on metric names, types, and labels.
