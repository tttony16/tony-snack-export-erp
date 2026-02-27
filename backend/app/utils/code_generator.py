from datetime import date


def generate_order_no(prefix: str, date_val: date, sequence: int) -> str:
    """Generate business code like SO-20260227-001 or PO-20260227-001."""
    return f"{prefix}-{date_val.strftime('%Y%m%d')}-{sequence:03d}"


def generate_entity_code(prefix: str, sequence: int) -> str:
    """Generate entity code like CUS-0001 or SUP-0001."""
    return f"{prefix}-{sequence:04d}"
