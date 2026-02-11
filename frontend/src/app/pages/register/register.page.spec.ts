import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, convertToParamMap, Router } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService, LoginResponse } from '../../core/auth/auth.service';
import { ToastService } from '../../core/ui/toast.service';
import { RegisterPage } from './register.page';

describe('RegisterPage', () => {
  const authServiceMock = {
    isAuthenticated: vi.fn(() => false),
    register: vi.fn(),
    clearSession: vi.fn(),
  };

  const toastMock = {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  };

  const routerMock = {
    navigateByUrl: vi.fn(() => Promise.resolve(true)),
    navigate: vi.fn(() => Promise.resolve(true)),
  };

  beforeEach(async () => {
    authServiceMock.isAuthenticated.mockReturnValue(false);
    authServiceMock.register.mockReset();
    authServiceMock.clearSession.mockReset();
    toastMock.success.mockReset();
    toastMock.error.mockReset();
    toastMock.info.mockReset();
    routerMock.navigateByUrl.mockClear();
    routerMock.navigate.mockClear();

    await TestBed.configureTestingModule({
      imports: [RegisterPage],
      providers: [
        { provide: AuthService, useValue: authServiceMock },
        { provide: ToastService, useValue: toastMock },
        { provide: Router, useValue: routerMock },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { queryParamMap: convertToParamMap({}) } },
        },
      ],
    }).compileComponents();
  });

  it('should show error toast and skip API when passwords do not match', () => {
    const fixture = TestBed.createComponent(RegisterPage);
    const component = fixture.componentInstance;

    component.form.setValue({
      name: 'user',
      email: 'user@example.com',
      password: '12345678',
      confirmPassword: '87654321',
    });
    component.onSubmit();

    expect(authServiceMock.register).not.toHaveBeenCalled();
    expect(toastMock.error).toHaveBeenCalledWith('As senhas nao conferem.');
  });

  it('should call register, show success toast, and redirect on success', () => {
    const fixture = TestBed.createComponent(RegisterPage);
    const component = fixture.componentInstance;

    const registerResponse: LoginResponse = {
      access_token: 'token',
      token_type: 'Bearer',
      expires_in: 3600,
    };
    authServiceMock.register.mockReturnValue(of(registerResponse));

    component.form.setValue({
      name: 'user',
      email: 'USER@example.com',
      password: '12345678',
      confirmPassword: '12345678',
    });
    component.onSubmit();

    expect(authServiceMock.register).toHaveBeenCalledWith(
      'user',
      'user@example.com',
      '12345678',
    );
    expect(authServiceMock.clearSession).toHaveBeenCalled();
    expect(toastMock.success).toHaveBeenCalledWith(
      'Conta criada com sucesso. Faca login para continuar.',
    );
    expect(routerMock.navigate).toHaveBeenCalledWith(['/login'], {
      queryParams: { created: '1' },
    });
  });

  it('should show specific toast for duplicated email', () => {
    const fixture = TestBed.createComponent(RegisterPage);
    const component = fixture.componentInstance;

    authServiceMock.register.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 409,
            error: { error: 'email_already_exists' },
          }),
      ),
    );

    component.form.setValue({
      name: 'user',
      email: 'user@example.com',
      password: '12345678',
      confirmPassword: '12345678',
    });
    component.onSubmit();

    expect(toastMock.error).toHaveBeenCalledWith('E-mail ja cadastrado.');
  });
});
