"""Test data factories for creating model instances."""

import uuid

from app.models.enums import (
    CurrencyType,
    PaymentMethod,
    ProductCategory,
)


def make_product_data(**overrides) -> dict:
    defaults = {
        "sku_code": f"SKU-{uuid.uuid4().hex[:8].upper()}",
        "name_cn": "测试零食",
        "name_en": "Test Snack",
        "category": ProductCategory.CANDY.value,
        "brand": "测试品牌",
        "spec": "500g/袋",
        "unit_weight_kg": "0.550",
        "unit_volume_cbm": "0.001200",
        "packing_spec": "24袋/箱",
        "carton_length_cm": "40.00",
        "carton_width_cm": "30.00",
        "carton_height_cm": "25.00",
        "carton_gross_weight_kg": "13.500",
        "shelf_life_days": 365,
    }
    defaults.update(overrides)
    return defaults


def make_customer_data(**overrides) -> dict:
    defaults = {
        "name": f"Test Customer {uuid.uuid4().hex[:6]}",
        "country": "Thailand",
        "contact_person": "John Doe",
        "currency": CurrencyType.USD.value,
        "payment_method": PaymentMethod.TT.value,
    }
    defaults.update(overrides)
    return defaults


def make_supplier_data(**overrides) -> dict:
    defaults = {
        "name": f"Test Supplier {uuid.uuid4().hex[:6]}",
        "contact_person": "Jane Supplier",
        "phone": "13800138000",
    }
    defaults.update(overrides)
    return defaults
