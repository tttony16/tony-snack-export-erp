import type {
  ProductStatus,
  SalesOrderStatus,
  PurchaseOrderStatus,
  InspectionResult,
  ContainerPlanStatus,
  ContainerType,
  LogisticsStatus,
  LogisticsCostType,
  UserRole,
  CurrencyType,
  PaymentMethod,
  TradeTerm,
  UnitType,
  AuditAction,
} from './api';

// ===== Auth =====

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

// ===== User =====

export interface UserRead {
  id: string;
  username: string;
  display_name: string;
  email: string | null;
  phone: string | null;
  role: UserRole;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  password: string;
  display_name: string;
  email?: string;
  phone?: string;
  role?: UserRole;
}

export interface UserUpdate {
  display_name?: string;
  email?: string;
  phone?: string;
  role?: UserRole;
  is_active?: boolean;
}

// ===== Product Category =====

export interface ProductCategoryRead {
  id: string;
  name: string;
  level: number;
  parent_id: string | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ProductCategoryTreeNode extends ProductCategoryRead {
  children: ProductCategoryTreeNode[];
}

// ===== Product =====

export interface ProductRead {
  id: string;
  sku_code: string;
  name_cn: string;
  name_en: string;
  category_id: string;
  category_level1_name: string | null;
  category_level2_name: string | null;
  category_level3_name: string | null;
  brand: string | null;
  barcode: string | null;
  spec: string;
  unit_weight_kg: number;
  unit_volume_cbm: number;
  packing_spec: string;
  carton_length_cm: number;
  carton_width_cm: number;
  carton_height_cm: number;
  carton_gross_weight_kg: number;
  shelf_life_days: number;
  default_purchase_price: number | null;
  default_supplier_id: string | null;
  hs_code: string | null;
  image_url: string | null;
  status: ProductStatus;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  sku_code: string;
  name_cn: string;
  name_en: string;
  category_id: string;
  brand?: string;
  barcode?: string;
  spec: string;
  unit_weight_kg: number;
  unit_volume_cbm: number;
  packing_spec: string;
  carton_length_cm: number;
  carton_width_cm: number;
  carton_height_cm: number;
  carton_gross_weight_kg: number;
  shelf_life_days: number;
  default_purchase_price?: number;
  default_supplier_id?: string;
  hs_code?: string;
  image_url?: string;
  remark?: string;
}

export interface ProductUpdate {
  name_cn?: string;
  name_en?: string;
  category_id?: string;
  brand?: string;
  barcode?: string;
  spec?: string;
  unit_weight_kg?: number;
  unit_volume_cbm?: number;
  packing_spec?: string;
  carton_length_cm?: number;
  carton_width_cm?: number;
  carton_height_cm?: number;
  carton_gross_weight_kg?: number;
  shelf_life_days?: number;
  default_purchase_price?: number;
  default_supplier_id?: string;
  hs_code?: string;
  image_url?: string;
  remark?: string;
}

export interface ProductListParams {
  keyword?: string;
  category_id?: string;
  brand?: string;
  status?: ProductStatus;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ===== Customer =====

export interface CustomerRead {
  id: string;
  customer_code: string;
  name: string;
  short_name: string | null;
  country: string;
  address: string | null;
  contact_person: string;
  phone: string | null;
  email: string | null;
  currency: CurrencyType;
  payment_method: PaymentMethod;
  payment_terms: string | null;
  trade_term: TradeTerm | null;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerCreate {
  name: string;
  short_name?: string;
  country: string;
  address?: string;
  contact_person: string;
  phone?: string;
  email?: string;
  currency: CurrencyType;
  payment_method: PaymentMethod;
  payment_terms?: string;
  trade_term?: TradeTerm;
  remark?: string;
}

export interface CustomerUpdate {
  name?: string;
  short_name?: string;
  country?: string;
  address?: string;
  contact_person?: string;
  phone?: string;
  email?: string;
  currency?: CurrencyType;
  payment_method?: PaymentMethod;
  payment_terms?: string;
  trade_term?: TradeTerm;
  remark?: string;
}

export interface CustomerListParams {
  keyword?: string;
  country?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ===== Supplier =====

export interface SupplierRead {
  id: string;
  supplier_code: string;
  name: string;
  contact_person: string;
  phone: string;
  address: string | null;
  supply_categories: string[] | null;
  supply_brands: string[] | null;
  payment_terms: string | null;
  business_license: string | null;
  food_production_license: string | null;
  certificate_urls: string[] | null;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface SupplierCreate {
  name: string;
  contact_person: string;
  phone: string;
  address?: string;
  supply_categories?: string[];
  supply_brands?: string[];
  payment_terms?: string;
  business_license?: string;
  food_production_license?: string;
  certificate_urls?: string[];
  remark?: string;
}

export interface SupplierUpdate {
  name?: string;
  contact_person?: string;
  phone?: string;
  address?: string;
  supply_categories?: string[];
  supply_brands?: string[];
  payment_terms?: string;
  business_license?: string;
  food_production_license?: string;
  certificate_urls?: string[];
  remark?: string;
}

export interface SupplierProductCreate {
  product_id: string;
  supply_price?: number;
  remark?: string;
}

export interface SupplierProductRead {
  id: string;
  supplier_id: string;
  product_id: string;
  supply_price: number | null;
  remark: string | null;
  created_at: string;
}

export interface SupplierListParams {
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ===== Sales Order =====

export interface SalesOrderItemCreate {
  product_id: string;
  quantity: number;
  unit: UnitType;
  unit_price: number;
}

export interface SalesOrderItemRead {
  id: string;
  sales_order_id: string;
  product_id: string;
  quantity: number;
  unit: UnitType;
  unit_price: number;
  amount: number;
  purchased_quantity: number;
  received_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface SalesOrderCreate {
  customer_id: string;
  order_date: string;
  required_delivery_date?: string;
  destination_port: string;
  trade_term: TradeTerm;
  currency: CurrencyType;
  payment_method: PaymentMethod;
  payment_terms?: string;
  estimated_volume_cbm?: number;
  estimated_weight_kg?: number;
  remark?: string;
  items: SalesOrderItemCreate[];
}

export interface SalesOrderUpdate {
  customer_id?: string;
  order_date?: string;
  required_delivery_date?: string;
  destination_port?: string;
  trade_term?: TradeTerm;
  currency?: CurrencyType;
  payment_method?: PaymentMethod;
  payment_terms?: string;
  estimated_volume_cbm?: number;
  estimated_weight_kg?: number;
  remark?: string;
  items?: SalesOrderItemCreate[];
}

export interface SalesOrderRead {
  id: string;
  order_no: string;
  customer_id: string;
  order_date: string;
  required_delivery_date: string | null;
  destination_port: string;
  trade_term: TradeTerm;
  currency: CurrencyType;
  payment_method: PaymentMethod;
  payment_terms: string | null;
  status: SalesOrderStatus;
  total_amount: number;
  total_quantity: number;
  estimated_volume_cbm: number | null;
  estimated_weight_kg: number | null;
  remark: string | null;
  items: SalesOrderItemRead[];
  created_at: string;
  updated_at: string;
}

export interface SalesOrderListRead {
  id: string;
  order_no: string;
  customer_id: string;
  order_date: string;
  required_delivery_date: string | null;
  destination_port: string;
  trade_term: TradeTerm;
  currency: CurrencyType;
  payment_method: PaymentMethod;
  status: SalesOrderStatus;
  total_amount: number;
  total_quantity: number;
  purchase_progress: number | null;
  arrival_progress: number | null;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface SalesOrderListParams {
  keyword?: string;
  status?: SalesOrderStatus;
  customer_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface KanbanItem {
  status: SalesOrderStatus;
  count: number;
  total_amount: number;
}

export interface KanbanResponse {
  items: KanbanItem[];
}

// ===== Purchase Order =====

export interface PurchaseOrderItemCreate {
  product_id: string;
  sales_order_item_id?: string;
  quantity: number;
  unit: UnitType;
  unit_price: number;
}

export interface PurchaseOrderItemRead {
  id: string;
  purchase_order_id: string;
  product_id: string;
  sales_order_item_id: string | null;
  quantity: number;
  unit: UnitType;
  unit_price: number;
  amount: number;
  received_quantity: number;
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrderCreate {
  supplier_id: string;
  order_date: string;
  required_date?: string;
  remark?: string;
  sales_order_ids?: string[];
  items: PurchaseOrderItemCreate[];
}

export interface PurchaseOrderUpdate {
  supplier_id?: string;
  order_date?: string;
  required_date?: string;
  remark?: string;
  items?: PurchaseOrderItemCreate[];
}

export interface PurchaseOrderRead {
  id: string;
  order_no: string;
  supplier_id: string;
  order_date: string;
  required_date: string | null;
  status: PurchaseOrderStatus;
  total_amount: number;
  remark: string | null;
  items: PurchaseOrderItemRead[];
  linked_sales_order_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrderListRead {
  id: string;
  order_no: string;
  supplier_id: string;
  order_date: string;
  required_date: string | null;
  status: PurchaseOrderStatus;
  total_amount: number;
  remark: string | null;
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrderListParams {
  keyword?: string;
  status?: PurchaseOrderStatus;
  supplier_id?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface LinkSalesOrdersRequest {
  sales_order_ids: string[];
}

// ===== Warehouse =====

export interface ReceivingNoteItemCreate {
  purchase_order_item_id: string;
  product_id: string;
  expected_quantity: number;
  actual_quantity: number;
  inspection_result: InspectionResult;
  failed_quantity?: number;
  failure_reason?: string;
  production_date: string;
  remark?: string;
}

export interface ReceivingNoteItemRead {
  id: string;
  receiving_note_id: string;
  purchase_order_item_id: string;
  product_id: string;
  expected_quantity: number;
  actual_quantity: number;
  inspection_result: InspectionResult;
  failed_quantity: number;
  failure_reason: string | null;
  production_date: string;
  batch_no: string;
  remark: string | null;
}

export interface ReceivingNoteCreate {
  purchase_order_id: string;
  receiving_date: string;
  receiver: string;
  remark?: string;
  items: ReceivingNoteItemCreate[];
}

export interface ReceivingNoteUpdate {
  receiving_date?: string;
  receiver?: string;
  remark?: string;
  items?: ReceivingNoteItemCreate[];
}

export interface ReceivingNoteRead {
  id: string;
  note_no: string;
  purchase_order_id: string;
  receiving_date: string;
  receiver: string;
  remark: string | null;
  items: ReceivingNoteItemRead[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ReceivingNoteListRead {
  id: string;
  note_no: string;
  purchase_order_id: string;
  receiving_date: string;
  receiver: string;
  created_at: string | null;
}

export interface ReceivingNoteListParams {
  purchase_order_id?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface InventoryRecordRead {
  id: string;
  product_id: string;
  sales_order_id: string | null;
  receiving_note_item_id: string;
  batch_no: string;
  production_date: string;
  quantity: number;
  available_quantity: number;
  created_at: string | null;
}

export interface InventoryByProductRead {
  product_id: string;
  total_quantity: number;
  available_quantity: number;
}

export interface InventoryByOrderRead {
  sales_order_id: string;
  product_id: string;
  total_quantity: number;
  available_quantity: number;
}

export interface InventoryListParams {
  product_id?: string;
  sales_order_id?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ReadinessCheckResponse {
  sales_order_id: string;
  is_ready: boolean;
  items: Record<string, unknown>[];
}

// ===== Container =====

export interface ContainerPlanItemCreate {
  container_seq: number;
  product_id: string;
  sales_order_id: string;
  quantity: number;
  volume_cbm: number;
  weight_kg: number;
}

export interface ContainerPlanItemRead {
  id: string;
  container_plan_id: string;
  container_seq: number;
  product_id: string;
  sales_order_id: string;
  quantity: number;
  volume_cbm: number;
  weight_kg: number;
}

export interface ContainerPlanItemUpdate {
  container_seq?: number;
  quantity?: number;
  volume_cbm?: number;
  weight_kg?: number;
}

export interface ContainerPlanCreate {
  sales_order_ids: string[];
  container_type: ContainerType;
  container_count?: number;
  destination_port?: string;
  remark?: string;
}

export interface ContainerPlanUpdate {
  container_type?: ContainerType;
  container_count?: number;
  destination_port?: string;
  remark?: string;
}

export interface ContainerStuffingPhotoRead {
  id: string;
  stuffing_record_id: string;
  photo_url: string;
  description: string | null;
}

export interface ContainerStuffingRecordRead {
  id: string;
  container_plan_id: string;
  container_seq: number;
  container_no: string;
  seal_no: string;
  stuffing_date: string;
  stuffing_location: string | null;
  remark: string | null;
  photos: ContainerStuffingPhotoRead[];
}

export interface ContainerPlanRead {
  id: string;
  plan_no: string;
  container_type: ContainerType;
  container_count: number;
  destination_port: string;
  status: ContainerPlanStatus;
  remark: string | null;
  items: ContainerPlanItemRead[];
  linked_sales_order_ids: string[];
  stuffing_records: ContainerStuffingRecordRead[];
  created_at: string | null;
  updated_at: string | null;
}

export interface ContainerPlanListRead {
  id: string;
  plan_no: string;
  container_type: ContainerType;
  container_count: number;
  destination_port: string;
  status: ContainerPlanStatus;
  created_at: string | null;
}

export interface ContainerPlanListParams {
  status?: ContainerPlanStatus;
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ContainerSummaryItem {
  container_seq: number;
  loaded_volume_cbm: number;
  volume_utilization: number;
  loaded_weight_kg: number;
  weight_utilization: number;
  is_over_volume: boolean;
  is_over_weight: boolean;
  item_count: number;
}

export interface ContainerSummaryResponse {
  items: ContainerSummaryItem[];
}

export interface ContainerRecommendation {
  container_type: string;
  count: number;
  volume_utilization: number;
  weight_utilization: number;
}

export interface ContainerRecommendationResponse {
  total_volume_cbm: number;
  total_weight_kg: number;
  recommendations: ContainerRecommendation[];
}

export interface ContainerStuffingCreate {
  container_seq: number;
  container_no: string;
  seal_no: string;
  stuffing_date: string;
  stuffing_location?: string;
  remark?: string;
}

export interface ContainerStuffingPhotoCreate {
  photo_url: string;
  description?: string;
}

export interface ContainerValidationResponse {
  is_valid: boolean;
  errors: Record<string, unknown>[];
  warnings: Record<string, unknown>[];
}

// ===== Logistics =====

export interface LogisticsCostCreate {
  cost_type: LogisticsCostType;
  amount: number;
  currency: CurrencyType;
  remark?: string;
}

export interface LogisticsCostRead {
  id: string;
  logistics_record_id: string;
  cost_type: LogisticsCostType;
  amount: number;
  currency: CurrencyType;
  remark: string | null;
}

export interface LogisticsCostUpdate {
  cost_type?: LogisticsCostType;
  amount?: number;
  currency?: CurrencyType;
  remark?: string;
}

export interface LogisticsRecordCreate {
  container_plan_id: string;
  shipping_company?: string;
  vessel_voyage?: string;
  bl_no?: string;
  port_of_loading: string;
  port_of_discharge?: string;
  etd?: string;
  eta?: string;
  actual_departure_date?: string;
  actual_arrival_date?: string;
  customs_declaration_no?: string;
  remark?: string;
}

export interface LogisticsRecordUpdate {
  shipping_company?: string;
  vessel_voyage?: string;
  bl_no?: string;
  port_of_loading?: string;
  port_of_discharge?: string;
  etd?: string;
  eta?: string;
  actual_departure_date?: string;
  actual_arrival_date?: string;
  customs_declaration_no?: string;
  remark?: string;
}

export interface LogisticsRecordRead {
  id: string;
  logistics_no: string;
  container_plan_id: string;
  shipping_company: string | null;
  vessel_voyage: string | null;
  bl_no: string | null;
  port_of_loading: string;
  port_of_discharge: string;
  etd: string | null;
  eta: string | null;
  actual_departure_date: string | null;
  actual_arrival_date: string | null;
  status: LogisticsStatus;
  customs_declaration_no: string | null;
  total_cost: number;
  remark: string | null;
  costs: LogisticsCostRead[];
  created_at: string | null;
  updated_at: string | null;
}

export interface LogisticsRecordListRead {
  id: string;
  logistics_no: string;
  container_plan_id: string;
  shipping_company: string | null;
  vessel_voyage: string | null;
  bl_no: string | null;
  port_of_loading: string;
  port_of_discharge: string;
  etd: string | null;
  eta: string | null;
  status: LogisticsStatus;
  total_cost: number;
  created_at: string | null;
}

export interface LogisticsRecordListParams {
  status?: LogisticsStatus;
  container_plan_id?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface LogisticsKanbanItem {
  status: LogisticsStatus;
  count: number;
  total_cost: number;
}

export interface LogisticsKanbanResponse {
  items: LogisticsKanbanItem[];
}

// ===== System =====

export interface SystemUserCreate {
  username: string;
  password: string;
  display_name: string;
  email?: string;
  phone?: string;
  role?: UserRole;
}

export interface SystemUserUpdate {
  display_name?: string;
  email?: string;
  phone?: string;
}

export interface AuditLogRead {
  id: number;
  user_id: string | null;
  action: AuditAction;
  resource_type: string;
  resource_id: string | null;
  detail: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogListParams {
  user_id?: string;
  action?: AuditAction;
  resource_type?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SystemConfigRead {
  id: number;
  config_key: string;
  config_value: unknown;
  description: string | null;
  updated_at: string;
  updated_by: string | null;
}

export interface SystemConfigUpdate {
  config_value: unknown;
  description?: string;
}

// ===== Dashboard =====

export interface OverviewItem {
  status: string;
  count: number;
  total_amount: number;
}

export interface OverviewResponse {
  sales_orders: OverviewItem[];
  purchase_orders: OverviewItem[];
}

export interface TodoResponse {
  draft_sales_orders: number;
  ordered_purchase_orders: number;
  goods_ready_sales_orders: number;
  arriving_soon_containers: number;
}

export interface InTransitItem {
  logistics_id: string;
  logistics_no: string;
  container_plan_id: string;
  status: string;
  shipping_company: string | null;
  vessel_voyage: string | null;
  eta: string | null;
  created_at: string | null;
}

export interface InTransitResponse {
  items: InTransitItem[];
  total: number;
}

export interface ExpiryWarningItem {
  product_id: string;
  product_name: string | null;
  batch_no: string;
  production_date: string;
  shelf_life_days: number;
  remaining_days: number;
  remaining_ratio: number;
  sales_order_id: string | null;
  quantity: number;
}

export interface ExpiryWarningResponse {
  threshold: number;
  items: ExpiryWarningItem[];
}

// ===== Statistics =====

export interface SalesSummaryItem {
  group_key: string;
  order_count: number;
  total_amount: number;
}

export interface SalesSummaryResponse {
  items: SalesSummaryItem[];
}

export interface PurchaseSummaryItem {
  group_key: string;
  order_count: number;
  total_amount: number;
}

export interface PurchaseSummaryResponse {
  items: PurchaseSummaryItem[];
}

export interface ContainerSummaryStatItem {
  group_key: string;
  plan_count: number;
  container_count: number;
}

export interface ContainerSummaryStatResponse {
  items: ContainerSummaryStatItem[];
}

export interface CustomerRankingItem {
  customer_id: string;
  customer_name: string | null;
  order_count: number;
  total_amount: number;
}

export interface CustomerRankingResponse {
  items: CustomerRankingItem[];
}

export interface ProductRankingItem {
  product_id: string;
  product_name: string | null;
  total_quantity: number;
  total_amount: number;
}

export interface ProductRankingResponse {
  items: ProductRankingItem[];
}
