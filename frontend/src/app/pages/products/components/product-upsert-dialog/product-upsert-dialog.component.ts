import { Component, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

import { ProductUpsertPayload } from '../../../../core/products/products.types';
import { ProductFormComponent, ProductFormMode } from '../product-form/product-form.component';

export interface ProductUpsertDialogData {
  mode: ProductFormMode;
  title: string;
  subtitle: string;
  initialValue: ProductUpsertPayload | null;
}

@Component({
  selector: 'app-product-upsert-dialog',
  imports: [MatDialogModule, ProductFormComponent],
  templateUrl: './product-upsert-dialog.component.html',
  styleUrl: './product-upsert-dialog.component.css',
})
export class ProductUpsertDialogComponent {
  protected readonly data = inject<ProductUpsertDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<ProductUpsertDialogComponent>);

  protected onSave(payload: ProductUpsertPayload): void {
    this.dialogRef.close(payload);
  }

  protected onCancel(): void {
    this.dialogRef.close(undefined);
  }
}
