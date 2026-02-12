import { Component, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';

export interface ConfirmDeleteDialogData {
  productName: string;
}

@Component({
  selector: 'app-confirm-delete-dialog',
  imports: [MatDialogModule, MatButtonModule],
  templateUrl: './confirm-delete-dialog.component.html',
  styleUrl: './confirm-delete-dialog.component.css',
})
export class ConfirmDeleteDialogComponent {
  protected readonly data = inject<ConfirmDeleteDialogData>(MAT_DIALOG_DATA);
  private readonly dialogRef = inject(MatDialogRef<ConfirmDeleteDialogComponent>);

  protected cancel(): void {
    this.dialogRef.close(false);
  }

  protected confirm(): void {
    this.dialogRef.close(true);
  }
}
