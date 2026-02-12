import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { ProductUpsertPayload } from '../../../../core/products/products.types';

export type ProductFormMode = 'create' | 'edit';

@Component({
  selector: 'app-product-form',
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './product-form.component.html',
  styleUrl: './product-form.component.css',
})
export class ProductFormComponent implements OnChanges {
  private readonly formBuilder = inject(FormBuilder);

  @Input() mode: ProductFormMode = 'create';
  @Input() initialValue: ProductUpsertPayload | null = null;
  @Input() isSubmitting = false;
  @Input() showCancelButton = false;
  @Input() cancelLabel = 'Cancelar';

  @Output() save = new EventEmitter<ProductUpsertPayload>();
  @Output() cancelEdit = new EventEmitter<void>();

  readonly form = this.formBuilder.group({
    nome: ['', [Validators.required]],
    marca: ['', [Validators.required]],
    valor: [null as number | null, [Validators.required, Validators.min(0.01)]],
  });
  readonly controls = this.form.controls;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mode'] || changes['initialValue']) {
      this.syncFormWithInputs();
    }
    if (changes['isSubmitting']) {
      this.syncFormDisabledState();
    }
  }

  onSubmit(): void {
    if (this.isSubmitting) {
      return;
    }

    this.form.markAllAsTouched();
    if (this.form.invalid) {
      return;
    }

    const nome = this.controls.nome.value?.trim() ?? '';
    const marca = this.controls.marca.value?.trim() ?? '';
    const valor = this.controls.valor.value ?? 0;

    if (!nome || !marca || valor <= 0) {
      return;
    }

    this.save.emit({
      nome,
      marca,
      valor,
    });
  }

  onCancelEdit(): void {
    this.cancelEdit.emit();
  }

  private syncFormWithInputs(): void {
    if (this.mode === 'edit' && this.initialValue) {
      this.form.reset(
        {
          nome: this.initialValue.nome,
          marca: this.initialValue.marca,
          valor: this.initialValue.valor,
        },
        { emitEvent: false },
      );
      this.form.markAsPristine();
      this.form.markAsUntouched();
      return;
    }

    this.form.reset(
      {
        nome: '',
        marca: '',
        valor: null,
      },
      { emitEvent: false },
    );
    this.form.markAsPristine();
    this.form.markAsUntouched();
  }

  private syncFormDisabledState(): void {
    if (this.isSubmitting) {
      this.form.disable({ emitEvent: false });
      return;
    }
    this.form.enable({ emitEvent: false });
  }
}
