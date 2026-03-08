"""
Entity schema definitions — replaces SQLAlchemy model classes.

Each schema defines the mutable fields for an entity type.
IDs and timestamps are managed by the GitStore service.
"""

ENTITY_SCHEMAS = {
    "hardware": {
        "fields": [
            "name", "hostname", "ip_address", "mac_address", "cpu", "cpu_cores",
            "ram_gb", "os", "make", "model", "serial_number", "location", "icon", "notes",
        ],
        "required": ["name"],
    },
    "vms": {
        "fields": [
            "hardware_id", "name", "hostname", "ip_address", "mac_address",
            "cpu_cores", "ram_gb", "disk_gb", "os", "icon", "notes",
        ],
        "required": ["name", "hardware_id"],
    },
    "apps": {
        "fields": [
            "hardware_id", "vm_id", "name", "description", "hostname", "ip_address",
            "external_hostname", "port", "https", "icon", "notes",
        ],
        "required": ["name"],
    },
    "storage": {
        "fields": [
            "hardware_id", "vm_id", "name", "storage_type", "raid_type", "drive_count",
            "raw_space_tb", "usable_space_tb", "filesystem", "icon", "notes",
        ],
        "required": ["name"],
    },
    "shares": {
        "fields": ["storage_id", "name", "hostname", "ip", "share_type", "notes"],
        "required": ["name", "storage_id"],
    },
    "networks": {
        "fields": ["name", "vlan_id", "subnet", "gateway", "dns_servers", "color", "notes"],
        "required": ["name"],
    },
    "documents": {
        "fields": ["parent_id", "title", "content", "sort_order"],
        "required": [],
    },
    "misc": {
        "fields": [
            "name", "category", "hostname", "description", "ip_address",
            "properties", "icon", "notes",
        ],
        "required": ["name"],
    },
}

# Entity types that use the CRUD factory
CRUD_ENTITY_TYPES = list(ENTITY_SCHEMAS.keys())


def clean_entity_data(entity_type: str, data: dict) -> dict:
    """Strip unknown fields and read-only fields from input data."""
    schema = ENTITY_SCHEMAS.get(entity_type)
    if schema is None:
        return data
    allowed = set(schema["fields"])
    return {k: v for k, v in data.items() if k in allowed}
