import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { ProductsApiService } from './products-api.service';
import { ProductUpsertPayload, ProductsListQuery } from './products.types';

describe('ProductsApiService', () => {
  let service: ProductsApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ProductsApiService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ProductsApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should call GET /api/products with offset and limit', () => {
    const query: ProductsListQuery = {
      offset: 20,
      limit: 10,
    };

    service.listProducts(query).subscribe((response) => {
      expect(response.items).toEqual([]);
      expect(response.total).toBe(32);
      expect(response.offset).toBe(20);
      expect(response.limit).toBe(10);
    });

    const request = httpMock.expectOne('/api/products?offset=20&limit=10');
    expect(request.request.method).toBe('GET');
    request.flush([], {
      headers: { 'X-Total-Count': '32' },
    });
  });

  it('should call POST /api/products', () => {
    const payload: ProductUpsertPayload = {
      nome: 'Mouse',
      marca: 'ACME',
      valor: 100,
    };

    service.createProduct(payload).subscribe();

    const request = httpMock.expectOne('/api/products');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    request.flush({
      status: 'queued',
      operation: 'create',
      operation_id: 'op-1',
    });
  });

  it('should call PUT /api/products/:id', () => {
    const payload: ProductUpsertPayload = {
      nome: 'Teclado',
      marca: 'ACME',
      valor: 120,
    };

    service.updateProduct(5, payload).subscribe();

    const request = httpMock.expectOne('/api/products/5');
    expect(request.request.method).toBe('PUT');
    expect(request.request.body).toEqual(payload);
    request.flush({
      status: 'queued',
      operation: 'update',
      operation_id: 'op-2',
      product_id: 5,
    });
  });

  it('should call DELETE /api/products/:id', () => {
    service.deleteProduct(8).subscribe();

    const request = httpMock.expectOne('/api/products/8');
    expect(request.request.method).toBe('DELETE');
    request.flush({
      status: 'queued',
      operation: 'delete',
      operation_id: 'op-3',
      product_id: 8,
    });
  });
});
