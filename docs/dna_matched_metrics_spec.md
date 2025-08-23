# Hive Standard Metrics Specification: DNA-Matched Metrics

## 1. Introduction

This document defines the standard for metrics instrumentation within a Hive-based architecture. The "DNA-Matched Metrics" standard ensures that all components emit a consistent, predictable set of metrics based on their fundamental primitive type (their "DNA").

This standardization is crucial for the `hive-physics` library, as it allows the library to query and interpret metrics from any Hive system to calculate its physical properties, such as Component Mass, Hive Temperature, and more. Adherence to this standard is required for a component to be fully "observable" by the Hive's physical laws.

## 2. Guiding Principles

- **Semantic Naming:** Metric names are prefixed with `hive_dna_` to indicate they are part of this standard. The name reflects the primitive type and the action being measured.
- **Consistent Labeling:** All metrics must include a standard set of labels to identify the source component. The primary label is `component_name`.
- **Primitive-Centric:** Each metric is tied directly to an action performed by one of the core ATCG primitives.

## 3. Core Primitive Metrics

### 3.1 Component Properties

These metrics define the intrinsic physical properties of a component.

| Metric Name | Type | Description | Required Labels |
| :--- | :--- | :--- | :--- |
| `hive_dna_component_charge` | Gauge | The electromagnetic charge of the component (+1, 0, -1). | `component_name` |

### 3.2 Aggregate (A)

Aggregates are the stateful, command-processing heart of the Hive.

| Metric Name | Type | Description | Required Labels |
| :--- | :--- | :--- | :--- |
| `hive_dna_aggregate_commands_handled_total` | Counter | Incremented every time an aggregate successfully handles a command. | `component_name` |
| `hive_dna_aggregate_command_failures_total` | Counter | Incremented every time an aggregate fails to handle a command. | `component_name`, `reason` |

### 3.3 Genesis Event (G)

Genesis Events are the result of state changes within Aggregates. Their emission is a key observable.

| Metric Name | Type | Description | Required Labels |
| :--- | :--- | :--- | :--- |
| `hive_dna_genesis_events_emitted_total` | Counter | Incremented by an Aggregate every time it emits a Genesis Event. | `component_name`, `event_type` |

### 3.4 Connector (C)

Connectors are the bridge to the outside world. We distinguish between primary (inbound) and secondary (outbound) connectors.

| Metric Name | Type | Description | Required Labels |
| :--- | :--- | :--- | :--- |
| `hive_dna_connector_requests_received_total` | Counter | (Primary) Incremented for each inbound request received. | `component_name`, `protocol` |
| `hive_dna_connector_requests_sent_total` | Counter | (Secondary) Incremented for each outbound request sent. | `component_name`, `destination` |
| `hive_dna_connector_request_latency_seconds` | Histogram | (Secondary) Measures the latency of outbound requests. | `component_name`, `destination` |

### 3.5 Transformation (T)

Transformations are stateless functions that perform calculations.

| Metric Name | Type | Description | Required Labels |
| :--- | :--- | :--- | :--- |
| `hive_dna_transformations_executed_total` | Counter | Incremented each time a transformation function is successfully executed. | `component_name` |
| `hive_dna_transformation_duration_seconds` | Histogram | Measures the execution time of the transformation. | `component_name` |

## 4. Application in Hive Physics

This standardized metrics system provides the foundation for calculating physical properties.

**Example: Calculating Component "Mass"**

The "mass" of a component is defined as its event throughput or processing rate. With DNA-Matched Metrics, we can calculate this precisely.

- **Mass of an Aggregate:** The rate of commands it handles.
  - **PromQL Query:** `rate(hive_dna_aggregate_commands_handled_total{component_name="OrderAggregate"}[5m])`

- **Mass of a Primary Connector:** The rate of requests it receives.
  - **PromQL Query:** `rate(hive_dna_connector_requests_received_total{component_name="RestAPI"}[5m])`

By adhering to this specification, any Hive system becomes immediately compatible with the `hive-physics` analysis and simulation tools.
