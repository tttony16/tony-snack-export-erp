"""Test data factories for creating model instances."""

import uuid
from datetime import date

from app.models.enums import (
    CurrencyType,
    PaymentMethod,
    ProductCategory,
    TradeTerm,
    UnitType,
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


def make_sales_order_data(customer_id: str, product_id: str, **overrides) -> dict:
    defaults = {
        "customer_id": customer_id,
        "order_date": date.today().isoformat(),
        "destination_port": "Bangkok Port",
        "trade_term": TradeTerm.FOB.value,
        "currency": CurrencyType.USD.value,
        "payment_method": PaymentMethod.TT.value,
        "items": [
            {
                "product_id": product_id,
                "quantity": 100,
                "unit": UnitType.CARTON.value,
                "unit_price": "25.50",
            }
        ],
    }
    defaults.update(overrides)
    return defaults


def make_purchase_order_data(supplier_id: str, product_id: str, **overrides) -> dict:
    defaults = {
        "supplier_id": supplier_id,
        "order_date": date.today().isoformat(),
        "items": [
            {
                "product_id": product_id,
                "quantity": 50,
                "unit": UnitType.CARTON.value,
                "unit_price": "20.00",
            }
        ],
        "sales_order_ids": [],
    }
    defaults.update(overrides)
    return defaults
