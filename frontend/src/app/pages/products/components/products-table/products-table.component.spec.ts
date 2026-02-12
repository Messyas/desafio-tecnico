import { LOCALE_ID } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { registerLocaleData } from '@angular/common';
import localePt from '@angular/common/locales/pt';
import { vi } from 'vitest';
import { PageEvent } from '@angular/material/paginator';

import { Product } from '../../../../core/products/products.types';
import { ProductsTableComponent } from './products-table.component';

describe('ProductsTableComponent', () => {
  const products: Product[] = [
    {
      id: 1,
      nome: 'Mouse',
      marca: 'ACME',
      valor: 99.9,
      created_at: '2026-02-11T00:00:00Z',
      updated_at: '2026-02-11T00:00:00Z',
    },
  ];

  beforeEach(async () => {
    registerLocaleData(localePt);

    await TestBed.configureTestingModule({
      imports: [ProductsTableComponent],
      providers: [{ provide: LOCALE_ID, useValue: 'pt-BR' }],
    }).compileComponents();
  });

  it('should render product rows', () => {
    const fixture = TestBed.createComponent(ProductsTableComponent);
    const component = fixture.componentInstance;
    component.products = products;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Mouse');
    expect(compiled.textContent).toContain('ACME');
  });

  it('should emit editProduct when clicking edit button', () => {
    const fixture = TestBed.createComponent(ProductsTableComponent);
    const component = fixture.componentInstance;
    const editSpy = vi.fn();
    component.editProduct.subscribe(editSpy);
    component.products = products;
    fixture.detectChanges();

    const editButton = fixture.nativeElement.querySelector('[data-testid="edit-product-1"]');
    editButton.click();

    expect(editSpy).toHaveBeenCalledWith(products[0]);
  });

  it('should emit deleteProduct when clicking delete button', () => {
    const fixture = TestBed.createComponent(ProductsTableComponent);
    const component = fixture.componentInstance;
    const deleteSpy = vi.fn();
    component.deleteProduct.subscribe(deleteSpy);
    component.products = products;
    fixture.detectChanges();

    const deleteButton = fixture.nativeElement.querySelector('[data-testid="delete-product-1"]');
    deleteButton.click();

    expect(deleteSpy).toHaveBeenCalledWith(products[0]);
  });

  it('should emit pageChange with offset and limit', () => {
    const fixture = TestBed.createComponent(ProductsTableComponent);
    const component = fixture.componentInstance;
    const pageSpy = vi.fn();
    component.pageChange.subscribe(pageSpy);

    const pageEvent: PageEvent = {
      pageIndex: 2,
      pageSize: 20,
      length: 50,
      previousPageIndex: 1,
    };
    component.onPageChanged(pageEvent);

    expect(pageSpy).toHaveBeenCalledWith({
      offset: 40,
      limit: 20,
    });
  });
});
