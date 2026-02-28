from enum import Enum


class Permission(str, Enum):
    # 商品
    PRODUCT_VIEW = "product:view"
    PRODUCT_EDIT = "product:edit"
    PRODUCT_IMPORT = "product:import"
    PRODUCT_EXPORT = "product:export"
    # 客户
    CUSTOMER_VIEW = "customer:view"
    CUSTOMER_EDIT = "customer:edit"
    CUSTOMER_EXPORT = "customer:export"
    # 供应商
    SUPPLIER_VIEW = "supplier:view"
    SUPPLIER_EDIT = "supplier:edit"
    SUPPLIER_EXPORT = "supplier:export"
    # 销售订单
    SALES_ORDER_VIEW = "sales_order:view"
    SALES_ORDER_EDIT = "sales_order:edit"
    SALES_ORDER_CONFIRM = "sales_order:confirm"
    SALES_ORDER_EXPORT = "sales_order:export"
    # 采购单
    PURCHASE_ORDER_VIEW = "purchase_order:view"
    PURCHASE_ORDER_EDIT = "purchase_order:edit"
    PURCHASE_ORDER_CONFIRM = "purchase_order:confirm"
    # 仓储
    WAREHOUSE_OPERATE = "warehouse:operate"
    INVENTORY_VIEW = "inventory:view"
    # 排柜
    CONTAINER_VIEW = "container:view"
    CONTAINER_EDIT = "container:edit"
    CONTAINER_CONFIRM = "container:confirm"
    CONTAINER_STUFFING = "container:stuffing"
    PACKING_LIST_EXPORT = "packing_list:export"
    # 出库
    OUTBOUND_VIEW = "outbound:view"
    OUTBOUND_EDIT = "outbound:edit"
    OUTBOUND_CONFIRM = "outbound:confirm"
    # 物流
    LOGISTICS_VIEW = "logistics:view"
    LOGISTICS_EDIT = "logistics:edit"
    # 系统
    USER_MANAGE = "user:manage"
    AUDIT_LOG_VIEW = "audit_log:view"
    SYSTEM_CONFIG = "system:config"
    STATISTICS_VIEW = "statistics:view"


ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "super_admin": set(Permission),
    "admin": {
        Permission.PRODUCT_VIEW,
        Permission.PRODUCT_EDIT,
        Permission.PRODUCT_IMPORT,
        Permission.CUSTOMER_VIEW,
        Permission.CUSTOMER_EDIT,
        Permission.SUPPLIER_VIEW,
        Permission.SUPPLIER_EDIT,
        Permission.SALES_ORDER_VIEW,
        Permission.SALES_ORDER_EDIT,
        Permission.SALES_ORDER_CONFIRM,
        Permission.PURCHASE_ORDER_VIEW,
        Permission.PURCHASE_ORDER_EDIT,
        Permission.PURCHASE_ORDER_CONFIRM,
        Permission.WAREHOUSE_OPERATE,
        Permission.INVENTORY_VIEW,
        Permission.CONTAINER_VIEW,
        Permission.CONTAINER_EDIT,
        Permission.CONTAINER_CONFIRM,
        Permission.CONTAINER_STUFFING,
        Permission.PACKING_LIST_EXPORT,
        Permission.OUTBOUND_VIEW,
        Permission.OUTBOUND_EDIT,
        Permission.OUTBOUND_CONFIRM,
        Permission.LOGISTICS_VIEW,
        Permission.LOGISTICS_EDIT,
        Permission.AUDIT_LOG_VIEW,
        Permission.STATISTICS_VIEW,
    },
    "sales": {
        Permission.PRODUCT_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.CUSTOMER_EDIT,
        Permission.SALES_ORDER_VIEW,
        Permission.SALES_ORDER_EDIT,
        Permission.PURCHASE_ORDER_VIEW,
        Permission.INVENTORY_VIEW,
        Permission.CONTAINER_VIEW,
        Permission.CONTAINER_EDIT,
        Permission.PACKING_LIST_EXPORT,
        Permission.LOGISTICS_VIEW,
        Permission.LOGISTICS_EDIT,
    },
    "purchaser": {
        Permission.PRODUCT_VIEW,
        Permission.SUPPLIER_VIEW,
        Permission.SUPPLIER_EDIT,
        Permission.SALES_ORDER_VIEW,
        Permission.PURCHASE_ORDER_VIEW,
        Permission.PURCHASE_ORDER_EDIT,
        Permission.INVENTORY_VIEW,
    },
    "warehouse": {
        Permission.PRODUCT_VIEW,
        Permission.SALES_ORDER_VIEW,
        Permission.INVENTORY_VIEW,
        Permission.WAREHOUSE_OPERATE,
        Permission.CONTAINER_VIEW,
        Permission.CONTAINER_STUFFING,
        Permission.PACKING_LIST_EXPORT,
        Permission.OUTBOUND_VIEW,
        Permission.OUTBOUND_EDIT,
        Permission.OUTBOUND_CONFIRM,
    },
    "viewer": {
        Permission.PRODUCT_VIEW,
        Permission.CUSTOMER_VIEW,
        Permission.SUPPLIER_VIEW,
        Permission.SALES_ORDER_VIEW,
        Permission.PURCHASE_ORDER_VIEW,
        Permission.INVENTORY_VIEW,
        Permission.CONTAINER_VIEW,
        Permission.OUTBOUND_VIEW,
        Permission.LOGISTICS_VIEW,
    },
}
