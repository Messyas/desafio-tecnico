export interface Product {
  id: number;
  nome: string;
  marca: string;
  valor: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface ProductUpsertPayload {
  nome: string;
  marca: string;
  valor: number;
}

export interface ProductsListQuery {
  offset: number;
  limit: number;
}

export interface ProductsListResponse {
  items: Product[];
  total: number;
  offset: number;
  limit: number;
}

export type ProductOperationType = 'create' | 'update' | 'delete';

export interface QueuedProductOperationResponse {
  status: 'queued';
  operation: ProductOperationType;
  operation_id: string;
  product_id?: number;
}

export interface ProductsQueryState {
  isLoading: boolean;
  isPolling: boolean;
  errorMessage: string | null;
}
