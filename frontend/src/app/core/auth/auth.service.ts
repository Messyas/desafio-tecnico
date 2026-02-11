import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, of, timeout } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

const AUTH_STORAGE_KEY = 'auth_access_token';
const AUTH_API_BASE_PATH = '/api/auth';
const AUTH_REQUEST_TIMEOUT_MS = 10000;

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private token: string | null = this.readTokenFromStorage();

  login(identifier: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${AUTH_API_BASE_PATH}/login`, {
        identifier,
        password,
      })
      .pipe(
        timeout(AUTH_REQUEST_TIMEOUT_MS),
        tap((response) => {
          this.persistLogin(response);
        }),
      );
  }

  register(name: string, email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${AUTH_API_BASE_PATH}/register`, {
        name,
        email,
        password,
      })
      .pipe(timeout(AUTH_REQUEST_TIMEOUT_MS));
  }

  logout(): Observable<void> {
    if (!this.token) {
      return of(void 0);
    }

    return this.http
      .post<{ status: string }>(`${AUTH_API_BASE_PATH}/logout`, {})
      .pipe(
        timeout(AUTH_REQUEST_TIMEOUT_MS),
        map(() => void 0),
        catchError(() => of(void 0)),
        tap(() => {
          this.clearToken();
        }),
      );
  }

  getToken(): string | null {
    return this.token;
  }

  isAuthenticated(): boolean {
    return this.token !== null;
  }

  clearSession(): void {
    this.clearToken();
  }

  private setToken(token: string): void {
    this.token = token;
    localStorage.setItem(AUTH_STORAGE_KEY, token);
  }

  private persistLogin(response: LoginResponse): void {
    this.setToken(response.access_token);
  }

  private clearToken(): void {
    this.token = null;
    localStorage.removeItem(AUTH_STORAGE_KEY);
  }

  private readTokenFromStorage(): string | null {
    const token = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!token) {
      return null;
    }

    const normalized = token.trim();
    return normalized.length > 0 ? normalized : null;
  }
}
