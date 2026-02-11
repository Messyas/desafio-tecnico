import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Params, Router, RouterLink } from '@angular/router';
import { TimeoutError as RxTimeoutError } from 'rxjs';
import { finalize, take } from 'rxjs/operators';

import { AuthService } from '../../core/auth/auth.service';
import { ToastService } from '../../core/ui/toast.service';

@Component({
  selector: 'app-login-page',
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './login.page.html',
  styleUrl: './login.page.css',
})
export class LoginPage {
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly toast = inject(ToastService);

  readonly form = this.formBuilder.group({
    identifier: ['', [Validators.required]],
    password: ['', [Validators.required]],
  });
  readonly controls = this.form.controls;

  readonly hidePassword = signal(true);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly feedbackMessage = signal<string | null>(null);

  constructor() {
    if (this.authService.isAuthenticated()) {
      void this.router.navigateByUrl('/products');
      return;
    }

    this.consumeRouteFeedback();
  }

  onSubmit(): void {
    if (this.isSubmitting()) {
      return;
    }

    this.form.markAllAsTouched();
    if (this.form.invalid) {
      const message = 'Preencha os campos corretamente.';
      this.errorMessage.set(message);
      this.showFeedback(message, 'error');
      return;
    }

    const identifier = this.controls.identifier.value.trim();
    const password = this.controls.password.value;
    if (!identifier || !password) {
      const message = 'Informe usuario/e-mail e senha.';
      this.errorMessage.set(message);
      this.showFeedback(message, 'error');
      return;
    }

    this.errorMessage.set(null);
    this.isSubmitting.set(true);

    this.authService
      .login(identifier, password)
      .pipe(
        take(1),
        finalize(() => this.isSubmitting.set(false)),
      )
      .subscribe({
        next: () => {
          this.showFeedback('Login realizado com sucesso.', 'success');
          void this.router.navigateByUrl(this.resolveRedirectUrl());
        },
        error: (error: unknown) => {
          const message = this.mapLoginError(error);
          this.errorMessage.set(message);
          this.showFeedback(message, 'error');
        },
      });
  }

  togglePasswordVisibility(): void {
    this.hidePassword.update((value) => !value);
  }

  private resolveRedirectUrl(): string {
    const redirectParam = this.route.snapshot.queryParamMap.get('redirect');
    if (redirectParam && redirectParam.startsWith('/')) {
      return redirectParam;
    }
    return '/products';
  }

  private mapLoginError(error: unknown): string {
    if (error instanceof RxTimeoutError) {
      return 'Servidor demorou para responder. Tente novamente.';
    }

    if (!(error instanceof HttpErrorResponse)) {
      return 'Nao foi possivel fazer login agora. Tente novamente.';
    }

    if (error.status === 401) {
      return 'Credenciais invalidas.';
    }

    const apiError = this.readApiError(error);
    if (apiError === 'invalid_payload') {
      return 'Preencha os campos corretamente.';
    }

    if (
      apiError === 'missing_token' ||
      apiError === 'invalid_token' ||
      apiError === 'expired_token'
    ) {
      return 'Sessao invalida. Faca login novamente.';
    }

    return 'Nao foi possivel fazer login agora. Tente novamente.';
  }

  private consumeRouteFeedback(): void {
    const queryParamMap = this.route.snapshot.queryParamMap;
    const shouldShowCreated = queryParamMap.get('created') === '1';
    const shouldShowLoggedOut = queryParamMap.get('loggedOut') === '1';
    if (!shouldShowCreated && !shouldShowLoggedOut) {
      return;
    }

    if (shouldShowCreated) {
      this.showFeedback('Conta criada com sucesso. Faca login para entrar.', 'success');
    }
    if (shouldShowLoggedOut) {
      this.showFeedback('Logout realizado com sucesso.', 'info');
    }

    const nextQueryParams: Params = {};
    const redirect = queryParamMap.get('redirect');
    if (redirect) {
      nextQueryParams['redirect'] = redirect;
    }

    void this.router.navigate([], {
      relativeTo: this.route,
      replaceUrl: true,
      queryParams: nextQueryParams,
    });
  }

  private showFeedback(message: string, variant: 'success' | 'error' | 'info'): void {
    this.feedbackMessage.set(message);
    if (variant === 'success') {
      this.toast.success(message);
      return;
    }
    if (variant === 'error') {
      this.toast.error(message);
      return;
    }
    this.toast.info(message);
  }

  private readApiError(error: HttpErrorResponse): string | null {
    const payload = error.error;
    if (!payload || typeof payload !== 'object') {
      return null;
    }

    const maybeError = (payload as { error?: unknown }).error;
    return typeof maybeError === 'string' ? maybeError : null;
  }
}
