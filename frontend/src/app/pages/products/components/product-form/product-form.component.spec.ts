import { TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { MatFormField } from '@angular/material/form-field';
import { vi } from 'vitest';

import { ProductFormComponent } from './product-form.component';

describe('ProductFormComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductFormComponent],
    }).compileComponents();
  });

  it('should not emit save when form is invalid', () => {
    const fixture = TestBed.createComponent(ProductFormComponent);
    const component = fixture.componentInstance;
    const saveSpy = vi.fn();
    component.save.subscribe(saveSpy);

    component.onSubmit();

    expect(saveSpy).not.toHaveBeenCalled();
  });

  it('should render three fields with always-visible labels', () => {
    const fixture = TestBed.createComponent(ProductFormComponent);
    fixture.detectChanges();

    const formFields = fixture.debugElement.queryAll(By.directive(MatFormField));

    expect(formFields).toHaveLength(3);
    for (const field of formFields) {
      const formFieldInstance = field.componentInstance as MatFormField;
      expect(formFieldInstance.floatLabel).toBe('always');
    }
  });

  it('should emit normalized payload when form is valid', () => {
    const fixture = TestBed.createComponent(ProductFormComponent);
    const component = fixture.componentInstance;
    const saveSpy = vi.fn();
    component.save.subscribe(saveSpy);

    component.form.setValue({
      nome: '  Mouse Gamer  ',
      marca: '  ACME ',
      valor: 250.5,
    });
    component.onSubmit();

    expect(saveSpy).toHaveBeenCalledWith({
      nome: 'Mouse Gamer',
      marca: 'ACME',
      valor: 250.5,
    });
  });

  it('should patch form when switching to edit mode', () => {
    const fixture = TestBed.createComponent(ProductFormComponent);
    const component = fixture.componentInstance;

    fixture.componentRef.setInput('mode', 'edit');
    fixture.componentRef.setInput('initialValue', {
      nome: 'Notebook',
      marca: 'Dell',
      valor: 3200,
    });
    fixture.detectChanges();

    expect(component.form.value).toEqual({
      nome: 'Notebook',
      marca: 'Dell',
      valor: 3200,
    });
  });

  it('should emit cancel event in edit mode', () => {
    const fixture = TestBed.createComponent(ProductFormComponent);
    const component = fixture.componentInstance;
    const cancelSpy = vi.fn();
    component.cancelEdit.subscribe(cancelSpy);

    component.onCancelEdit();

    expect(cancelSpy).toHaveBeenCalled();
  });
});
