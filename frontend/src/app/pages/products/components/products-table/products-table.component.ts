import { CurrencyPipe } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';

import { Product } from '../../../../core/products/products.types';

export interface ProductsPageChange {
  offset: number;
  limit: number;
}

@Component({
  selector: 'app-products-table',
  imports: [
    CurrencyPipe,
    MatTableModule,
    MatButtonModule,
    MatProgressBarModule,
    MatPaginatorModule,
  ],
  templateUrl: './products-table.component.html',
  styleUrl: './products-table.component.css',
})
export class ProductsTableComponent {
  @Input() products: Product[] = [];
  @Input() isLoading = false;
  @Input() deletingProductId: number | null = null;
  @Input() totalCount = 0;
  @Input() offset = 0;
  @Input() limit = 10;
  @Input() pageSizeOptions: number[] = [5, 10, 20, 50];
  @Input() disablePagination = false;

  @Output() editProduct = new EventEmitter<Product>();
  @Output() deleteProduct = new EventEmitter<Product>();
  @Output() pageChange = new EventEmitter<ProductsPageChange>();

  readonly displayedColumns = ['nome', 'marca', 'valor', 'actions'];

  get pageIndex(): number {
    if (this.limit <= 0) {
      return 0;
    }
    return Math.floor(this.offset / this.limit);
  }

  onEdit(product: Product): void {
    this.editProduct.emit(product);
  }

  onDelete(product: Product): void {
    this.deleteProduct.emit(product);
  }

  isDeleteDisabled(productId: number): boolean {
    return this.deletingProductId !== null && this.deletingProductId !== productId;
  }

  isDeleting(productId: number): boolean {
    return this.deletingProductId === productId;
  }

  onPageChanged(event: PageEvent): void {
    this.pageChange.emit({
      offset: event.pageIndex * event.pageSize,
      limit: event.pageSize,
    });
  }
}
