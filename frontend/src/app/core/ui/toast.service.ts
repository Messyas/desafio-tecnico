import { Injectable, inject } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';

type ToastType = 'toast-success' | 'toast-error' | 'toast-info';

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly snackBar = inject(MatSnackBar);

  success(message: string): void {
    this.open(message, 'toast-success');
  }

  error(message: string): void {
    this.open(message, 'toast-error');
  }

  info(message: string): void {
    this.open(message, 'toast-info');
  }

  private open(message: string, panelClass: ToastType): void {
    this.snackBar.open(message, 'Fechar', {
      duration: 4000,
      panelClass,
      horizontalPosition: 'right',
      verticalPosition: 'top',
    });
  }
}
