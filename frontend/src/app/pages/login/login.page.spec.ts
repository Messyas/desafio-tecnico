import { ActivatedRoute, convertToParamMap, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { vi } from 'vitest';

import { AuthService, LoginResponse } from '../../core/auth/auth.service';
import { ToastService } from '../../core/ui/toast.service';
import { LoginPage } from './login.page';

describe('LoginPage', () => {
  const authServiceMock = {
    isAuthenticated: vi.fn(() => false),
    login: vi.fn(),
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

  const activatedRouteMock = {
    snapshot: {
      queryParamMap: convertToParamMap({}),
    },
  };

  beforeEach(async () => {
    authServiceMock.isAuthenticated.mockReturnValue(false);
    authServiceMock.login.mockReset();
    toastMock.success.mockReset();
    toastMock.error.mockReset();
    toastMock.info.mockReset();
    routerMock.navigateByUrl.mockClear();
    routerMock.navigate.mockClear();

    await TestBed.configureTestingModule({
      imports: [LoginPage],
      providers: [
        { provide: AuthService, useValue: authServiceMock },
        { provide: ToastService, useValue: toastMock },
        { provide: Router, useValue: routerMock },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
      ],
    }).compileComponents();
  });

  it('should show error toast and avoid API call when form is invalid', () => {
    const fixture = TestBed.createComponent(LoginPage);
    const component = fixture.componentInstance;

    component.onSubmit();

    expect(authServiceMock.login).not.toHaveBeenCalled();
    expect(toastMock.error).toHaveBeenCalledWith('Preencha os campos corretamente.');
  });

  it('should call login and show success toast on valid submit', () => {
    const fixture = TestBed.createComponent(LoginPage);
    const component = fixture.componentInstance;

    const loginResponse: LoginResponse = {
      access_token: 'token',
      token_type: 'Bearer',
      expires_in: 3600,
    };
    authServiceMock.login.mockReturnValue(of(loginResponse));

    component.form.setValue({ identifier: ' user ', password: '12345678' });
    component.onSubmit();

    expect(authServiceMock.login).toHaveBeenCalledWith('user', '12345678');
    expect(toastMock.success).toHaveBeenCalledWith('Login realizado com sucesso.');
    expect(routerMock.navigateByUrl).toHaveBeenCalledWith('/products');
  });

  it('should show credentials error on 401 response', () => {
    const fixture = TestBed.createComponent(LoginPage);
    const component = fixture.componentInstance;

    authServiceMock.login.mockReturnValue(throwError(() => new HttpErrorResponse({ status: 401 })));

    component.form.setValue({ identifier: 'user', password: 'wrong' });
    component.onSubmit();

    expect(toastMock.error).toHaveBeenCalledWith('Credenciais invalidas.');
  });
});
