"""Magics Component Parameter Definition — canonical Altium facet names per category.

Mirrors the team spec (Component Parameter Definition). InvenTree template names may
differ; see Backend ``ALTIUM_VALUE_SOURCE_ALIASES`` for Altium → InvenTree mapping.
"""

from __future__ import annotations

# Parent-level Electronic Components parameters (Altium names).
ELECTRONIC_COMPONENTS_BASE: tuple[str, ...] = (
    "Max/Min Operating Temperature",
    "Rad-hardness",
    "RoHS",
    "Lifecycle Status",
)

PASSIVES_BASE: tuple[str, ...] = (
    "Value",
    "Package",
    "Height (max)",
    "Tolerance",
)

IC_BASE: tuple[str, ...] = (
    "Manufacturer",
    "Package",
    "Height",
    "Supply voltage",
)

CONNECTOR_BASE: tuple[str, ...] = (
    "Pins",
    "Pitch",
    "Max current",
    "Material",
    "Plating",
    "Wire size",
    "IP Rating",
)

DISCRETE_BASE: tuple[str, ...] = (
    "Package",
    "Max open voltage",
    "Max Current",
    "Channels",
)

# All unique spec parameter names referenced in the Electronic Components tree.
ALL_SPEC_PARAMETER_NAMES: frozenset[str] = frozenset(
    {
        *ELECTRONIC_COMPONENTS_BASE,
        *PASSIVES_BASE,
        "Power (max)",
        "Temperature Coefficient",
        "Technology",
        "Voltage",
        "Dielectric",
        "ESR",
        "Saturation Current",
        "Rated current",
        "DCR",
        "Resonant Frequency",
        "Blow Type",
        "Resistance",
        "Fuse Type",
        "Impedance",
        "Test Frequency",
        "Number of Turns",
        "Orientation",
        "Element Type",
        "Taper",
        "Primary voltage",
        "Power Rating",
        "Turns Ratio",
        "Isolation voltage",
        "Frequency",
        "Type",
        "Output Signal",
        "Response Time",
        *IC_BASE,
        "channels",
        "Amplification",
        "Core types",
        "ROM size",
        "RAM size",
        "IOs",
        "Max clock speed",
        "Cells",
        "Size",
        "Interface type",
        "Resolution",
        "Sample speed",
        "Supply voltage analog",
        "Protocol",
        "Logic levels",
        "Propagation Delay",
        "Outputs",
        "Power ratings",
        "Communication Interface",
        "Current Limit",
        "Frequency Band",
        "Output power",
        *CONNECTOR_BASE,
        "Rows",
        "Row pitch",
        "Amount",
        "Shielded",
        "Leds",
        "Connector Type",
        "Frequency Range",
        "Current rating",
        "Voltage rating",
        "Locking system",
        "Series",
        "IP rating",
        "Keying",
        "Shell material",
        *DISCRETE_BASE,
        "Color",
        "Forward voltage",
        "Luminous intensity",
        "Gain (β)",
        "Rds(on)",
        "Gate capacitance",
        "Breakdown voltage",
        "Forward Voltage",
        "Reverse Recovery Time",
        "ESD voltage rating",
        "Isolation voltage",
        "CTR",
        "Coil voltage",
        "Coil current",
        "Contact current",
        "Contact voltage",
        "Contact type",
        "Contact Rating",
        "Actuation Force",
        "Speed",
        "Torque",
        "Airflow",
        "Static pressure",
        "Stability",
        "Load capacitance",
        "Shunt capacitance",
        "Current",
        "Output",
        "Control Voltage",
        "Phase Noise",
        "Manufacturer Part Number",
        "Description",
    }
)

# Sample folder prefixes used when auditing components per major branch.
AUDIT_FOLDER_PREFIXES: tuple[str, ...] = (
    "Electronic Components/Passives/Capacitors",
    "Electronic Components/Passives/Resistors",
    "Electronic Components/ICs",
    "Electronic Components/Connectors",
    "Electronic Components/Discrete Semiconductors",
    "Electronic Components/Crystals&Oscillators",
)
