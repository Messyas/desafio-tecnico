import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { vi } from 'vitest';

import { App } from './app';
import { AuthService } from './core/auth/auth.service';

describe('App', () => {
  const authServiceMock = {
    isAuthenticated: vi.fn(() => false),
    logout: vi.fn(() => of(void 0)),
  };

  beforeEach(async () => {
    authServiceMock.isAuthenticated.mockReturnValue(false);
    authServiceMock.logout.mockClear();

    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), { provide: AuthService, useValue: authServiceMock }],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render title', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.app-navbar__brand')?.textContent).toContain('Desafio Tecnico');
  });
});
