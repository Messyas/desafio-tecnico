import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router, RouterLink } from '@angular/router';
import { TimeoutError as RxTimeoutError } from 'rxjs';
import { finalize, take } from 'rxjs/operators';

import { AuthService } from '../../core/auth/auth.service';
import { ToastService } from '../../core/ui/toast.service';

const MIN_PASSWORD_LENGTH = 8;

@Component({
  selector: 'app-register-page',
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
  templateUrl: './register.page.html',
  styleUrl: './register.page.css',
})
export class RegisterPage {
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  readonly form = this.formBuilder.group({
    name: ['', [Validators.required]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(MIN_PASSWORD_LENGTH)]],
    confirmPassword: ['', [Validators.required]],
  });
  readonly controls = this.form.controls;

  readonly hidePassword = signal(true);
  readonly isSubmitting = signal(false);
  readonly feedbackMessage = signal<string | null>(null);
  readonly feedbackVariant = signal<'success' | 'error' | 'info'>('info');

  constructor() {
    if (this.authService.isAuthenticated()) {
      void this.router.navigateByUrl('/products');
    }
  }

  onSubmit(): void {
    if (this.isSubmitting()) {
      return;
    }

    this.form.markAllAsTouched();
    if (this.form.invalid) {
      this.showFeedback('Verifique os campos obrigatorios.', 'error');
      return;
    }

    const name = this.controls.name.value.trim();
    const email = this.controls.email.value.trim().toLowerCase();
    const password = this.controls.password.value;
    const confirmPassword = this.controls.confirmPassword.value;
    if (!name || !email || !password || !confirmPassword) {
      this.showFeedback('Preencha todos os campos.', 'error');
      return;
    }

    if (password !== confirmPassword) {
      this.controls.confirmPassword.setErrors({ passwordMismatch: true });
      this.showFeedback('As senhas nao conferem.', 'error');
      return;
    }

    if (this.controls.confirmPassword.hasError('passwordMismatch')) {
      this.controls.confirmPassword.setErrors(null);
    }

    this.isSubmitting.set(true);

    this.authService
      .register(name, email, password)
      .pipe(
        take(1),
        finalize(() => this.isSubmitting.set(false)),
      )
      .subscribe({
        next: () => {
          this.authService.clearSession();
          this.showFeedback('Conta criada com sucesso. Faca login para continuar.', 'success');
          void this.router.navigate(['/login'], {
            queryParams: { created: '1' },
          });
        },
        error: (error: unknown) => {
          this.showFeedback(this.mapRegisterError(error), 'error');
        },
      });
  }

  togglePasswordVisibility(): void {
    this.hidePassword.update((value) => !value);
  }

  private mapRegisterError(error: unknown): string {
    if (error instanceof RxTimeoutError) {
      return 'Servidor demorou para responder. Tente novamente.';
    }

    if (!(error instanceof HttpErrorResponse)) {
      return 'Nao foi possivel concluir o cadastro agora.';
    }

    const apiError = this.readApiError(error);

    if (error.status === 409 && apiError === 'name_already_exists') {
      return 'Nome de usuario ja cadastrado.';
    }
    if (error.status === 409 && apiError === 'email_already_exists') {
      return 'E-mail ja cadastrado.';
    }
    if (apiError === 'password_too_short') {
      return 'A senha deve ter pelo menos 8 caracteres.';
    }
    if (apiError === 'invalid_payload') {
      return 'Dados invalidos. Verifique os campos.';
    }

    return 'Nao foi possivel concluir o cadastro agora.';
  }

  private showFeedback(message: string, variant: 'success' | 'error' | 'info'): void {
    this.feedbackMessage.set(message);
    this.feedbackVariant.set(variant);

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
