import enum


class ProductCategory(str, enum.Enum):
    PUFFED_FOOD = "puffed_food"
    CANDY = "candy"
    BISCUIT = "biscuit"
    NUT = "nut"
    BEVERAGE = "beverage"
    SEASONING = "seasoning"
    INSTANT_NOODLE = "instant_noodle"
    DRIED_FRUIT = "dried_fruit"
    CHOCOLATE = "chocolate"
    JELLY = "jelly"
    OTHER = "other"


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SalesOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    PURCHASING = "purchasing"
    GOODS_READY = "goods_ready"
    CONTAINER_PLANNED = "container_planned"
    CONTAINER_LOADED = "container_loaded"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    ABNORMAL = "abnormal"


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    ORDERED = "ordered"
    PARTIAL_RECEIVED = "partial_received"
    FULLY_RECEIVED = "fully_received"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InspectionResult(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL_PASSED = "partial_passed"


class ContainerPlanStatus(str, enum.Enum):
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    LOADING = "loading"
    LOADED = "loaded"
    SHIPPED = "shipped"


class ContainerType(str, enum.Enum):
    GP20 = "20GP"
    GP40 = "40GP"
    HQ40 = "40HQ"
    REEFER = "reefer"


class LogisticsStatus(str, enum.Enum):
    BOOKED = "booked"
    CUSTOMS_CLEARED = "customs_cleared"
    LOADED_ON_SHIP = "loaded_on_ship"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SALES = "sales"
    PURCHASER = "purchaser"
    WAREHOUSE = "warehouse"
    VIEWER = "viewer"


class CurrencyType(str, enum.Enum):
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    GBP = "GBP"
    THB = "THB"
    VND = "VND"
    MYR = "MYR"
    SGD = "SGD"
    PHP = "PHP"
    IDR = "IDR"
    RMB = "RMB"
    OTHER = "OTHER"


class PaymentMethod(str, enum.Enum):
    TT = "TT"
    LC = "LC"
    DP = "DP"
    DA = "DA"


class TradeTerm(str, enum.Enum):
    FOB = "FOB"
    CIF = "CIF"
    CFR = "CFR"
    EXW = "EXW"
    DDP = "DDP"
    DAP = "DAP"


class UnitType(str, enum.Enum):
    PIECE = "piece"
    CARTON = "carton"


class LogisticsCostType(str, enum.Enum):
    OCEAN_FREIGHT = "ocean_freight"
    CUSTOMS_FEE = "customs_fee"
    PORT_CHARGE = "port_charge"
    TRUCKING_FEE = "trucking_fee"
    INSURANCE_FEE = "insurance_fee"
    OTHER = "other"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    STATUS_CHANGE = "status_change"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
