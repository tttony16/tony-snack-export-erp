// ===== Generic Response Types =====

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  code: number;
  message: string;
  data: PaginatedData<T>;
}

export interface ListParams {
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ===== Enums =====

export const ProductCategory = {
  puffed_food: 'puffed_food',
  candy: 'candy',
  biscuit: 'biscuit',
  nut: 'nut',
  beverage: 'beverage',
  seasoning: 'seasoning',
  instant_noodle: 'instant_noodle',
  dried_fruit: 'dried_fruit',
  chocolate: 'chocolate',
  jelly: 'jelly',
  other: 'other',
} as const;
export type ProductCategory = (typeof ProductCategory)[keyof typeof ProductCategory];

export const ProductCategoryLabels: Record<ProductCategory, string> = {
  puffed_food: '膨化食品',
  candy: '糖果',
  biscuit: '饼干',
  nut: '坚果',
  beverage: '饮料',
  seasoning: '调味品',
  instant_noodle: '方便面',
  dried_fruit: '果干',
  chocolate: '巧克力',
  jelly: '果冻',
  other: '其他',
};

export const ProductStatus = {
  active: 'active',
  inactive: 'inactive',
} as const;
export type ProductStatus = (typeof ProductStatus)[keyof typeof ProductStatus];

export const ProductStatusLabels: Record<ProductStatus, string> = {
  active: '启用',
  inactive: '停用',
};

export const SalesOrderStatus = {
  draft: 'draft',
  confirmed: 'confirmed',
  purchasing: 'purchasing',
  goods_ready: 'goods_ready',
  container_planned: 'container_planned',
  container_loaded: 'container_loaded',
  shipped: 'shipped',
  delivered: 'delivered',
  completed: 'completed',
  abnormal: 'abnormal',
} as const;
export type SalesOrderStatus = (typeof SalesOrderStatus)[keyof typeof SalesOrderStatus];

export const SalesOrderStatusLabels: Record<SalesOrderStatus, string> = {
  draft: '草稿',
  confirmed: '已确认',
  purchasing: '采购中',
  goods_ready: '备货完成',
  container_planned: '已排柜',
  container_loaded: '已装柜',
  shipped: '已发货',
  delivered: '已送达',
  completed: '已完成',
  abnormal: '异常',
};

export const SalesOrderStatusColors: Record<SalesOrderStatus, string> = {
  draft: 'default',
  confirmed: 'blue',
  purchasing: 'cyan',
  goods_ready: 'geekblue',
  container_planned: 'purple',
  container_loaded: 'orange',
  shipped: 'gold',
  delivered: 'lime',
  completed: 'green',
  abnormal: 'red',
};

export const PurchaseOrderStatus = {
  draft: 'draft',
  ordered: 'ordered',
  partial_received: 'partial_received',
  fully_received: 'fully_received',
  completed: 'completed',
  cancelled: 'cancelled',
} as const;
export type PurchaseOrderStatus = (typeof PurchaseOrderStatus)[keyof typeof PurchaseOrderStatus];

export const PurchaseOrderStatusLabels: Record<PurchaseOrderStatus, string> = {
  draft: '草稿',
  ordered: '已下单',
  partial_received: '部分收货',
  fully_received: '全部收货',
  completed: '已完成',
  cancelled: '已取消',
};

export const PurchaseOrderStatusColors: Record<PurchaseOrderStatus, string> = {
  draft: 'default',
  ordered: 'blue',
  partial_received: 'orange',
  fully_received: 'cyan',
  completed: 'green',
  cancelled: 'red',
};

export const InspectionResult = {
  passed: 'passed',
  failed: 'failed',
  partial_passed: 'partial_passed',
} as const;
export type InspectionResult = (typeof InspectionResult)[keyof typeof InspectionResult];

export const InspectionResultLabels: Record<InspectionResult, string> = {
  passed: '合格',
  failed: '不合格',
  partial_passed: '部分合格',
};

export const InspectionResultColors: Record<InspectionResult, string> = {
  passed: 'green',
  failed: 'red',
  partial_passed: 'orange',
};

export const ContainerPlanStatus = {
  planning: 'planning',
  confirmed: 'confirmed',
  loading: 'loading',
  loaded: 'loaded',
  shipped: 'shipped',
} as const;
export type ContainerPlanStatus = (typeof ContainerPlanStatus)[keyof typeof ContainerPlanStatus];

export const ContainerPlanStatusLabels: Record<ContainerPlanStatus, string> = {
  planning: '计划中',
  confirmed: '已确认',
  loading: '装柜中',
  loaded: '已装柜',
  shipped: '已发运',
};

export const ContainerPlanStatusColors: Record<ContainerPlanStatus, string> = {
  planning: 'default',
  confirmed: 'blue',
  loading: 'orange',
  loaded: 'cyan',
  shipped: 'green',
};

export const ContainerType = {
  '20GP': '20GP',
  '40GP': '40GP',
  '40HQ': '40HQ',
  reefer: 'reefer',
} as const;
export type ContainerType = (typeof ContainerType)[keyof typeof ContainerType];

export const ContainerTypeLabels: Record<ContainerType, string> = {
  '20GP': '20尺普柜',
  '40GP': '40尺普柜',
  '40HQ': '40尺高柜',
  reefer: '冷藏柜',
};

export const LogisticsStatus = {
  booked: 'booked',
  customs_cleared: 'customs_cleared',
  loaded_on_ship: 'loaded_on_ship',
  in_transit: 'in_transit',
  arrived: 'arrived',
  picked_up: 'picked_up',
  delivered: 'delivered',
} as const;
export type LogisticsStatus = (typeof LogisticsStatus)[keyof typeof LogisticsStatus];

export const LogisticsStatusLabels: Record<LogisticsStatus, string> = {
  booked: '已订舱',
  customs_cleared: '已报关',
  loaded_on_ship: '已装船',
  in_transit: '在途',
  arrived: '已到港',
  picked_up: '已提柜',
  delivered: '已送达',
};

export const LogisticsStatusColors: Record<LogisticsStatus, string> = {
  booked: 'default',
  customs_cleared: 'blue',
  loaded_on_ship: 'cyan',
  in_transit: 'geekblue',
  arrived: 'orange',
  picked_up: 'lime',
  delivered: 'green',
};

export const UserRole = {
  super_admin: 'super_admin',
  admin: 'admin',
  sales: 'sales',
  purchaser: 'purchaser',
  warehouse: 'warehouse',
  viewer: 'viewer',
} as const;
export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export const UserRoleLabels: Record<UserRole, string> = {
  super_admin: '超级管理员',
  admin: '管理员',
  sales: '销售',
  purchaser: '采购',
  warehouse: '仓库',
  viewer: '查看者',
};

export const CurrencyType = {
  USD: 'USD',
  EUR: 'EUR',
  JPY: 'JPY',
  GBP: 'GBP',
  THB: 'THB',
  VND: 'VND',
  MYR: 'MYR',
  SGD: 'SGD',
  PHP: 'PHP',
  IDR: 'IDR',
  RMB: 'RMB',
  OTHER: 'OTHER',
} as const;
export type CurrencyType = (typeof CurrencyType)[keyof typeof CurrencyType];

export const CurrencyTypeLabels: Record<CurrencyType, string> = {
  USD: '美元 (USD)',
  EUR: '欧元 (EUR)',
  JPY: '日元 (JPY)',
  GBP: '英镑 (GBP)',
  THB: '泰铢 (THB)',
  VND: '越南盾 (VND)',
  MYR: '马来西亚林吉特 (MYR)',
  SGD: '新加坡元 (SGD)',
  PHP: '菲律宾比索 (PHP)',
  IDR: '印尼盾 (IDR)',
  RMB: '人民币 (RMB)',
  OTHER: '其他',
};

export const PaymentMethod = {
  TT: 'TT',
  LC: 'LC',
  DP: 'DP',
  DA: 'DA',
} as const;
export type PaymentMethod = (typeof PaymentMethod)[keyof typeof PaymentMethod];

export const PaymentMethodLabels: Record<PaymentMethod, string> = {
  TT: '电汇 (T/T)',
  LC: '信用证 (L/C)',
  DP: '付款交单 (D/P)',
  DA: '承兑交单 (D/A)',
};

export const TradeTerm = {
  FOB: 'FOB',
  CIF: 'CIF',
  CFR: 'CFR',
  EXW: 'EXW',
  DDP: 'DDP',
  DAP: 'DAP',
} as const;
export type TradeTerm = (typeof TradeTerm)[keyof typeof TradeTerm];

export const TradeTermLabels: Record<TradeTerm, string> = {
  FOB: 'FOB',
  CIF: 'CIF',
  CFR: 'CFR',
  EXW: 'EXW',
  DDP: 'DDP',
  DAP: 'DAP',
};

export const UnitType = {
  piece: 'piece',
  carton: 'carton',
} as const;
export type UnitType = (typeof UnitType)[keyof typeof UnitType];

export const UnitTypeLabels: Record<UnitType, string> = {
  piece: '件',
  carton: '箱',
};

export const LogisticsCostType = {
  ocean_freight: 'ocean_freight',
  customs_fee: 'customs_fee',
  port_charge: 'port_charge',
  trucking_fee: 'trucking_fee',
  insurance_fee: 'insurance_fee',
  other: 'other',
} as const;
export type LogisticsCostType = (typeof LogisticsCostType)[keyof typeof LogisticsCostType];

export const LogisticsCostTypeLabels: Record<LogisticsCostType, string> = {
  ocean_freight: '海运费',
  customs_fee: '报关费',
  port_charge: '港杂费',
  trucking_fee: '拖车费',
  insurance_fee: '保险费',
  other: '其他',
};

export const AuditAction = {
  create: 'create',
  update: 'update',
  delete: 'delete',
  export: 'export',
  status_change: 'status_change',
  login: 'login',
  logout: 'logout',
  permission_change: 'permission_change',
} as const;
export type AuditAction = (typeof AuditAction)[keyof typeof AuditAction];

export const AuditActionLabels: Record<AuditAction, string> = {
  create: '创建',
  update: '更新',
  delete: '删除',
  export: '导出',
  status_change: '状态变更',
  login: '登录',
  logout: '登出',
  permission_change: '权限变更',
};
