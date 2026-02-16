from app.exceptions import InvalidTransitionError

# Garment lifecycle transitions (forward + backward)
GARMENT_TRANSITIONS: dict[str, set[str]] = {
    "CONCEPT": {"DESIGN"},
    "DESIGN": {"CONCEPT", "DEVELOPMENT"},
    "DEVELOPMENT": {"DESIGN", "SAMPLING"},
    "SAMPLING": {"DEVELOPMENT", "PRODUCTION"},
    "PRODUCTION": set(),  # Terminal state - no exit
}

# Supplier pipeline transitions
SUPPLIER_TRANSITIONS: dict[str, set[str]] = {
    "OFFERED": {"SAMPLING", "REJECTED"},
    "SAMPLING": {"APPROVED", "REJECTED"},
    "APPROVED": {"IN_PRODUCTION", "REJECTED"},
    "REJECTED": set(),  # Terminal state
    "IN_PRODUCTION": {"IN_STORE"},
    "IN_STORE": set(),  # Terminal state
}


def validate_garment_transition(current_stage: str, target_stage: str) -> None:
    valid_targets = GARMENT_TRANSITIONS.get(current_stage, set())
    if target_stage not in valid_targets:
        raise InvalidTransitionError(current_stage, target_stage, sorted(valid_targets))


def validate_supplier_transition(current_status: str, target_status: str) -> None:
    valid_targets = SUPPLIER_TRANSITIONS.get(current_status, set())
    if target_status not in valid_targets:
        raise InvalidTransitionError(current_status, target_status, sorted(valid_targets))
