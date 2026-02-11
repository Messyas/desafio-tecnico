import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterOutlet } from '@angular/router';
import { finalize, take } from 'rxjs/operators';

import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MatToolbarModule, MatButtonModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly title = signal('Desafio Tecnico');
  protected readonly isLoggingOut = signal(false);

  protected shouldShowLogoutButton(): boolean {
    return this.authService.isAuthenticated() && this.router.url.startsWith('/products');
  }

  protected onLogout(): void {
    if (this.isLoggingOut()) {
      return;
    }

    this.isLoggingOut.set(true);
    this.authService
      .logout()
      .pipe(
        take(1),
        finalize(() => this.isLoggingOut.set(false)),
      )
      .subscribe({
        next: () => {
          void this.router.navigate(['/login'], {
            queryParams: { loggedOut: '1' },
          });
        },
      });
  }
}
