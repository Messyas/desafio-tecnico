import { HttpErrorResponse } from '@angular/common/http';
import { registerLocaleData } from '@angular/common';
import localePt from '@angular/common/locales/pt';
import { LOCALE_ID } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService } from '../../core/auth/auth.service';
import { ProductsApiService } from '../../core/products/products-api.service';
import { Product, ProductsListResponse } from '../../core/products/products.types';
import { ToastService } from '../../core/ui/toast.service';
import { ProductsPage } from './products.page';

describe('ProductsPage', () => {
  const productsApiServiceMock = {
    listProducts: vi.fn(),
    createProduct: vi.fn(),
    updateProduct: vi.fn(),
    deleteProduct: vi.fn(),
  };

  const authServiceMock = {
    clearSession: vi.fn(),
  };

  const toastMock = {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  };

  const routerMock = {
    navigate: vi.fn(() => Promise.resolve(true)),
  };

  const dialogMock = {
    open: vi.fn(),
  };

  const existingProduct: Product = {
    id: 1,
    nome: 'Mouse',
    marca: 'ACME',
    valor: 100,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  };

  const buildListResponse = (
    items: Product[],
    total: number,
    offset = 0,
    limit = 10,
  ): ProductsListResponse => ({
    items,
    total,
    offset,
    limit,
  });

  const waitForTimers = async (): Promise<void> => {
    await Promise.resolve();
    await new Promise((resolve) => setTimeout(resolve, 0));
  };

  beforeEach(async () => {
    registerLocaleData(localePt);

    productsApiServiceMock.listProducts.mockReset();
    productsApiServiceMock.createProduct.mockReset();
    productsApiServiceMock.updateProduct.mockReset();
    productsApiServiceMock.deleteProduct.mockReset();
    productsApiServiceMock.listProducts.mockReturnValue(of(buildListResponse([], 0)));

    authServiceMock.clearSession.mockReset();
    toastMock.success.mockReset();
    toastMock.error.mockReset();
    toastMock.info.mockReset();
    routerMock.navigate.mockClear();
    dialogMock.open.mockReset();

    TestBed.configureTestingModule({
      imports: [ProductsPage],
      providers: [
        { provide: LOCALE_ID, useValue: 'pt-BR' },
        { provide: ProductsApiService, useValue: productsApiServiceMock },
        { provide: AuthService, useValue: authServiceMock },
        { provide: ToastService, useValue: toastMock },
        { provide: Router, useValue: routerMock },
      ],
    });

    TestBed.overrideComponent(ProductsPage, {
      set: {
        providers: [{ provide: MatDialog, useValue: dialogMock }],
      },
    });

    await TestBed.compileComponents();
  });

  it('should load products on init with default offset/limit', () => {
    productsApiServiceMock.listProducts.mockReturnValueOnce(of(buildListResponse([existingProduct], 1)));

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    expect(productsApiServiceMock.listProducts).toHaveBeenCalledWith({ offset: 0, limit: 10 });
    expect(component.products()).toEqual([existingProduct]);
    expect(component.totalProducts()).toBe(1);
  });

  it('should open create modal and call createProduct', async () => {
    productsApiServiceMock.listProducts
      .mockReturnValueOnce(of(buildListResponse([], 0)))
      .mockReturnValueOnce(
        of(
          buildListResponse(
            [
              {
                ...existingProduct,
                id: 2,
                nome: 'Teclado',
              },
            ],
            1,
          ),
        ),
      );
    productsApiServiceMock.createProduct.mockReturnValue(
      of({
        status: 'queued',
        operation: 'create',
        operation_id: 'op-create',
      }),
    );
    dialogMock.open.mockReturnValue({
      afterClosed: () =>
        of({
          nome: 'Teclado',
          marca: 'ACME',
          valor: 150,
        }),
    });

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.onOpenCreateDialog();

    expect(dialogMock.open).toHaveBeenCalled();
    expect(productsApiServiceMock.createProduct).toHaveBeenCalledWith({
      nome: 'Teclado',
      marca: 'ACME',
      valor: 150,
    });

    await waitForTimers();
    expect(component.totalProducts()).toBe(1);
  });

  it('should open edit modal and call updateProduct', async () => {
    productsApiServiceMock.listProducts
      .mockReturnValueOnce(of(buildListResponse([existingProduct], 1)))
      .mockReturnValueOnce(
        of(
          buildListResponse(
            [
              {
                ...existingProduct,
                nome: 'Mouse Pro',
              },
            ],
            1,
          ),
        ),
      );
    productsApiServiceMock.updateProduct.mockReturnValue(
      of({
        status: 'queued',
        operation: 'update',
        operation_id: 'op-update',
        product_id: existingProduct.id,
      }),
    );
    dialogMock.open.mockReturnValue({
      afterClosed: () =>
        of({
          nome: 'Mouse Pro',
          marca: 'ACME',
          valor: 100,
        }),
    });

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.onEditProduct(existingProduct);

    expect(productsApiServiceMock.updateProduct).toHaveBeenCalledWith(existingProduct.id, {
      nome: 'Mouse Pro',
      marca: 'ACME',
      valor: 100,
    });

    await waitForTimers();
    expect(component.products()[0].nome).toBe('Mouse Pro');
  });

  it('should call deleteProduct after confirmation modal', async () => {
    productsApiServiceMock.listProducts
      .mockReturnValueOnce(of(buildListResponse([existingProduct], 1)))
      .mockReturnValueOnce(of(buildListResponse([], 0)));
    productsApiServiceMock.deleteProduct.mockReturnValue(
      of({
        status: 'queued',
        operation: 'delete',
        operation_id: 'op-delete',
        product_id: existingProduct.id,
      }),
    );
    dialogMock.open.mockReturnValue({
      afterClosed: () => of(true),
    });

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.onRequestDelete(existingProduct);

    expect(dialogMock.open).toHaveBeenCalled();
    expect(productsApiServiceMock.deleteProduct).toHaveBeenCalledWith(existingProduct.id);

    await waitForTimers();
    expect(component.totalProducts()).toBe(0);
  });

  it('should fetch a new page when paginator changes', () => {
    productsApiServiceMock.listProducts
      .mockReturnValueOnce(of(buildListResponse([existingProduct], 30, 0, 10)))
      .mockReturnValueOnce(of(buildListResponse([existingProduct], 30, 20, 10)));

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.onPageChange({ offset: 20, limit: 10 });

    expect(productsApiServiceMock.listProducts).toHaveBeenCalledWith({ offset: 20, limit: 10 });
  });

  it('should clear session and redirect on auth error', () => {
    productsApiServiceMock.listProducts.mockReturnValueOnce(of(buildListResponse([], 0)));
    productsApiServiceMock.createProduct.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 401,
            error: { error: 'invalid_token' },
          }),
      ),
    );
    dialogMock.open.mockReturnValue({
      afterClosed: () =>
        of({
          nome: 'Fone',
          marca: 'ACME',
          valor: 200,
        }),
    });

    const fixture = TestBed.createComponent(ProductsPage);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.onOpenCreateDialog();

    expect(authServiceMock.clearSession).toHaveBeenCalled();
    expect(routerMock.navigate).toHaveBeenCalledWith(['/login'], {
      queryParams: { redirect: '/products' },
    });
  });
});
