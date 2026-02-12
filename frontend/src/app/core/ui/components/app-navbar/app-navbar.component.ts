import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';

@Component({
  selector: 'app-navbar',
  imports: [MatToolbarModule, MatButtonModule],
  templateUrl: './app-navbar.component.html',
  styleUrl: './app-navbar.component.css',
})
export class AppNavbarComponent {
  @Input() title = '';
  @Input() showLogoutButton = false;
  @Input() isLoggingOut = false;

  @Output() logout = new EventEmitter<void>();

  protected onLogout(): void {
    this.logout.emit();
  }
}
