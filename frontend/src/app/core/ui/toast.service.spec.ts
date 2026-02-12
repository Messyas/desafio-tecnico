import { TestBed } from '@angular/core/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { vi } from 'vitest';

import { ToastService } from './toast.service';

describe('ToastService', () => {
  const snackBarMock = {
    open: vi.fn(),
  };

  beforeEach(() => {
    snackBarMock.open.mockReset();

    TestBed.configureTestingModule({
      providers: [ToastService, { provide: MatSnackBar, useValue: snackBarMock }],
    });
  });

  it('should open success toast with expected config', () => {
    const service = TestBed.inject(ToastService);

    service.success('Produto salvo.');

    expect(snackBarMock.open).toHaveBeenCalledWith('Produto salvo.', 'Fechar', {
      duration: 4000,
      panelClass: 'toast-success',
      horizontalPosition: 'right',
      verticalPosition: 'top',
    });
  });

  it('should open error toast with expected config', () => {
    const service = TestBed.inject(ToastService);

    service.error('Erro ao salvar.');

    expect(snackBarMock.open).toHaveBeenCalledWith('Erro ao salvar.', 'Fechar', {
      duration: 4000,
      panelClass: 'toast-error',
      horizontalPosition: 'right',
      verticalPosition: 'top',
    });
  });

  it('should open info toast with expected config', () => {
    const service = TestBed.inject(ToastService);

    service.info('Atualizando dados.');

    expect(snackBarMock.open).toHaveBeenCalledWith('Atualizando dados.', 'Fechar', {
      duration: 4000,
      panelClass: 'toast-info',
      horizontalPosition: 'right',
      verticalPosition: 'top',
    });
  });
});
