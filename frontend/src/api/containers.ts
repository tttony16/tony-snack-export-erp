import request from '@/utils/request';
import type { PaginatedData } from '@/types/api';
import type {
  ContainerPlanRead,
  ContainerPlanListRead,
  ContainerPlanCreate,
  ContainerPlanUpdate,
  ContainerPlanListParams,
  ContainerPlanItemCreate,
  ContainerPlanItemUpdate,
  ContainerPlanItemRead,
  ContainerSummaryResponse,
  ContainerRecommendationResponse,
  ContainerValidationResponse,
  ContainerStuffingCreate,
  ContainerStuffingRecordRead,
  ContainerStuffingPhotoCreate,
} from '@/types/models';

export async function listContainerPlans(params: ContainerPlanListParams): Promise<PaginatedData<ContainerPlanListRead>> {
  return request.get('/containers', { params });
}

export async function getContainerPlan(id: string): Promise<ContainerPlanRead> {
  return request.get(`/containers/${id}`);
}

export async function createContainerPlan(data: ContainerPlanCreate): Promise<ContainerPlanRead> {
  return request.post('/containers', data);
}

export async function updateContainerPlan(id: string, data: ContainerPlanUpdate): Promise<ContainerPlanRead> {
  return request.put(`/containers/${id}`, data);
}

export async function recommendContainerType(id: string): Promise<ContainerRecommendationResponse> {
  return request.post(`/containers/${id}/recommend-type`);
}

export async function addContainerItem(id: string, data: ContainerPlanItemCreate): Promise<ContainerPlanItemRead> {
  return request.post(`/containers/${id}/items`, data);
}

export async function updateContainerItem(id: string, itemId: string, data: ContainerPlanItemUpdate): Promise<ContainerPlanItemRead> {
  return request.put(`/containers/${id}/items/${itemId}`, data);
}

export async function removeContainerItem(id: string, itemId: string): Promise<void> {
  return request.delete(`/containers/${id}/items/${itemId}`);
}

export async function getContainerSummary(id: string): Promise<ContainerSummaryResponse> {
  return request.get(`/containers/${id}/summary`);
}

export async function validateContainer(id: string): Promise<ContainerValidationResponse> {
  return request.post(`/containers/${id}/validate`);
}

export async function confirmContainerPlan(id: string): Promise<ContainerPlanRead> {
  return request.post(`/containers/${id}/confirm`);
}

export async function cancelContainerPlan(id: string): Promise<ContainerPlanRead> {
  return request.post(`/containers/${id}/cancel`);
}

export async function recordStuffing(id: string, data: ContainerStuffingCreate): Promise<ContainerStuffingRecordRead> {
  return request.post(`/containers/${id}/stuffing`, data);
}

export async function uploadStuffingPhoto(id: string, data: ContainerStuffingPhotoCreate): Promise<unknown> {
  return request.post(`/containers/${id}/stuffing/photos`, data);
}

export async function getPackingList(id: string): Promise<unknown> {
  return request.get(`/containers/${id}/packing-list`);
}
