import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-products-page',
  imports: [MatCardModule],
  templateUrl: './products.page.html',
  styleUrl: './products.page.css',
})
export class ProductsPage {}
