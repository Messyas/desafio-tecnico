import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, timeout } from 'rxjs';
import { map } from 'rxjs/operators';

import {
  ProductsListQuery,
  ProductsListResponse,
  ProductUpsertPayload,
  QueuedProductOperationResponse,
} from './products.types';

const PRODUCTS_API_BASE_PATH = '/api/products';
const PRODUCTS_REQUEST_TIMEOUT_MS = 10000;

@Injectable({ providedIn: 'root' })
export class ProductsApiService {
  private readonly http = inject(HttpClient);

  listProducts(query: ProductsListQuery): Observable<ProductsListResponse> {
    const params = new HttpParams()
      .set('offset', String(query.offset))
      .set('limit', String(query.limit));

    return this.http
      .get<ProductsListResponse['items']>(PRODUCTS_API_BASE_PATH, {
        observe: 'response',
        params,
      })
      .pipe(
        timeout(PRODUCTS_REQUEST_TIMEOUT_MS),
        map((response) => {
          const items = response.body ?? [];
          const total = this.readTotalCountHeader(response.headers.get('X-Total-Count'), items.length);

          return {
            items,
            total,
            offset: query.offset,
            limit: query.limit,
          };
        }),
      );
  }

  createProduct(payload: ProductUpsertPayload): Observable<QueuedProductOperationResponse> {
    return this.http
      .post<QueuedProductOperationResponse>(PRODUCTS_API_BASE_PATH, payload)
      .pipe(timeout(PRODUCTS_REQUEST_TIMEOUT_MS));
  }

  updateProduct(
    productId: number,
    payload: ProductUpsertPayload,
  ): Observable<QueuedProductOperationResponse> {
    return this.http
      .put<QueuedProductOperationResponse>(`${PRODUCTS_API_BASE_PATH}/${productId}`, payload)
      .pipe(timeout(PRODUCTS_REQUEST_TIMEOUT_MS));
  }

  deleteProduct(productId: number): Observable<QueuedProductOperationResponse> {
    return this.http
      .delete<QueuedProductOperationResponse>(`${PRODUCTS_API_BASE_PATH}/${productId}`)
      .pipe(timeout(PRODUCTS_REQUEST_TIMEOUT_MS));
  }

  private readTotalCountHeader(headerValue: string | null, fallbackCount: number): number {
    if (headerValue === null) {
      return fallbackCount;
    }

    const parsed = Number.parseInt(headerValue, 10);
    if (!Number.isFinite(parsed) || parsed < 0) {
      return fallbackCount;
    }

    return parsed;
  }
}
