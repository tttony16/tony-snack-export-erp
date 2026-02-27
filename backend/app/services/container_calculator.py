"""Container type specifications and recommendation engine."""

import math
from decimal import Decimal

CONTAINER_SPECS: dict[str, dict] = {
    "20GP": {
        "volume_cbm": Decimal("33.2"),
        "max_weight_kg": Decimal("21800"),
        "length_cm": 590,
        "width_cm": 235,
        "height_cm": 239,
    },
    "40GP": {
        "volume_cbm": Decimal("67.7"),
        "max_weight_kg": Decimal("26680"),
        "length_cm": 1203,
        "width_cm": 235,
        "height_cm": 239,
    },
    "40HQ": {
        "volume_cbm": Decimal("76.3"),
        "max_weight_kg": Decimal("26580"),
        "length_cm": 1203,
        "width_cm": 235,
        "height_cm": 269,
    },
    "reefer": {
        "volume_cbm": Decimal("28.0"),
        "max_weight_kg": Decimal("27000"),
        "length_cm": 550,
        "width_cm": 228,
        "height_cm": 222,
    },
}


def recommend_container_type(total_volume_cbm: Decimal, total_weight_kg: Decimal) -> list[dict]:
    """Recommend container types based on total volume and weight."""
    recommendations = []
    for ctype, spec in CONTAINER_SPECS.items():
        if ctype == "reefer":
            continue  # reefer requires manual selection

        count_by_volume = math.ceil(float(total_volume_cbm) / float(spec["volume_cbm"]))
        count_by_weight = math.ceil(float(total_weight_kg) / float(spec["max_weight_kg"]))
        count = max(count_by_volume, count_by_weight, 1)

        volume_util = float(total_volume_cbm) / (float(spec["volume_cbm"]) * count) * 100
        weight_util = float(total_weight_kg) / (float(spec["max_weight_kg"]) * count) * 100

        recommendations.append(
            {
                "container_type": ctype,
                "count": count,
                "volume_utilization": round(Decimal(str(volume_util)), 1),
                "weight_utilization": round(Decimal(str(weight_util)), 1),
            }
        )

    recommendations.sort(
        key=lambda x: (x["count"], -max(x["volume_utilization"], x["weight_utilization"]))
    )
    return recommendations
