import request from '@/utils/request';
import type {
  SalesSummaryResponse,
  PurchaseSummaryResponse,
  ContainerSummaryStatResponse,
  CustomerRankingResponse,
  ProductRankingResponse,
} from '@/types/models';

interface SummaryParams {
  date_from?: string;
  date_to?: string;
  group_by?: string;
}

export async function getSalesSummary(params?: SummaryParams): Promise<SalesSummaryResponse> {
  return request.get('/statistics/sales-summary', { params });
}

export async function getPurchaseSummary(params?: SummaryParams): Promise<PurchaseSummaryResponse> {
  return request.get('/statistics/purchase-summary', { params });
}

export async function getContainerSummary(params?: SummaryParams): Promise<ContainerSummaryStatResponse> {
  return request.get('/statistics/container-summary', { params });
}

export async function getCustomerRanking(params?: SummaryParams): Promise<CustomerRankingResponse> {
  return request.get('/statistics/customer-ranking', { params });
}

export async function getProductRanking(params?: SummaryParams): Promise<ProductRankingResponse> {
  return request.get('/statistics/product-ranking', { params });
}
