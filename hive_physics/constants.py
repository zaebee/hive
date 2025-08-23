from dataclasses import dataclass

@dataclass(frozen=True)
class PhysicalConstants:
    """
    Holds the fundamental physical constants of the Hive universe.

    These values are considered immutable and universal across a single Hive.
    In a real implementation, these might be loaded from a configuration file.
    """
    G_HIVE: float = 0.01  # Component Attraction Constant
    K_HIVE: float = 1.38e-23  # Nectar Distribution Entropy Constant
    # The fine-structure constant for the Hive, representing the ratio of strong/weak bonds.
    ALPHA_HIVE_TARGET: float = 0.01
    # The default cosmological constant, representing a slow, stable growth rate.
    LAMBDA_HIVE_TARGET: float = 0.001
    # The Hive's electromagnetic constant, analogous to Coulomb's constant.
    K_HIVE_ELECTRO: float = 1.0
