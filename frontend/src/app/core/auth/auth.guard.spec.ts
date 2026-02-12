import { Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { vi } from 'vitest';

import { authGuard } from './auth.guard';
import { AuthService } from './auth.service';

describe('authGuard', () => {
  const authServiceMock = {
    isAuthenticated: vi.fn(() => false),
  };

  const routerMock = {
    createUrlTree: vi.fn(),
  };

  beforeEach(() => {
    authServiceMock.isAuthenticated.mockReset();
    routerMock.createUrlTree.mockReset();

    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authServiceMock },
        { provide: Router, useValue: routerMock },
      ],
    });
  });

  it('should allow route activation when authenticated', () => {
    authServiceMock.isAuthenticated.mockReturnValue(true);

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/products' } as RouterStateSnapshot),
    );

    expect(result).toBe(true);
    expect(routerMock.createUrlTree).not.toHaveBeenCalled();
  });

  it('should redirect to login with redirect query param when unauthenticated', () => {
    authServiceMock.isAuthenticated.mockReturnValue(false);
    const expectedTree = {} as UrlTree;
    routerMock.createUrlTree.mockReturnValue(expectedTree);

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/products' } as RouterStateSnapshot),
    );

    expect(routerMock.createUrlTree).toHaveBeenCalledWith(['/login'], {
      queryParams: { redirect: '/products' },
    });
    expect(result).toBe(expectedTree);
  });
});
