import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { Subscription, TimeoutError as RxTimeoutError, timer } from 'rxjs';
import { finalize, switchMap, take } from 'rxjs/operators';

import { AuthService } from '../../core/auth/auth.service';
import { ProductsApiService } from '../../core/products/products-api.service';
import {
  Product,
  ProductOperationType,
  ProductsListQuery,
  ProductsListResponse,
  ProductUpsertPayload,
  ProductsQueryState,
} from '../../core/products/products.types';
import { ToastService } from '../../core/ui/toast.service';
import {
  ConfirmDeleteDialogComponent,
  ConfirmDeleteDialogData,
} from './components/confirm-delete-dialog/confirm-delete-dialog.component';
import {
  ProductUpsertDialogComponent,
  ProductUpsertDialogData,
} from './components/product-upsert-dialog/product-upsert-dialog.component';
import { ProductsPageChange, ProductsTableComponent } from './components/products-table/products-table.component';

const POLL_INTERVAL_MS = 800;
const POLL_MAX_ATTEMPTS = 8;
const DEFAULT_PAGE_LIMIT = 10;
const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

const INITIAL_QUERY_STATE: ProductsQueryState = {
  isLoading: false,
  isPolling: false,
  errorMessage: null,
};

interface PaginationState {
  offset: number;
  limit: number;
  total: number;
}

interface PollExpectation {
  operation: ProductOperationType;
  previousTotal: number;
  query: ProductsListQuery;
  payload?: ProductUpsertPayload;
  productId?: number;
}

@Component({
  selector: 'app-products-page',
  imports: [MatCardModule, MatButtonModule, MatIconModule, ProductsTableComponent],
  templateUrl: './products.page.html',
  styleUrl: './products.page.css',
})
export class ProductsPage implements OnInit, OnDestroy {
  private readonly productsApiService = inject(ProductsApiService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly router = inject(Router);
  private readonly dialog = inject(MatDialog);

  private pollingSubscription: Subscription | null = null;

  readonly products = signal<Product[]>([]);
  readonly queryState = signal<ProductsQueryState>(INITIAL_QUERY_STATE);
  readonly pagination = signal<PaginationState>({
    offset: 0,
    limit: DEFAULT_PAGE_LIMIT,
    total: 0,
  });

  readonly isSaving = signal(false);
  readonly deletingProductId = signal<number | null>(null);

  readonly pageSizeOptions = PAGE_SIZE_OPTIONS;
  readonly totalProducts = computed(() => this.pagination().total);
  readonly isBusy = computed(() => this.isSaving() || this.deletingProductId() !== null);
  readonly isTableLoading = computed(() => this.queryState().isLoading || this.queryState().isPolling);

  ngOnInit(): void {
    this.fetchProducts(this.currentQuery(), true);
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  onRetryLoad(): void {
    this.fetchProducts(this.currentQuery(), true);
  }

  onOpenCreateDialog(): void {
    if (this.isBusy()) {
      return;
    }

    const dialogData: ProductUpsertDialogData = {
      mode: 'create',
      title: 'Novo produto',
      subtitle: 'Preencha os dados para cadastrar um produto.',
      initialValue: null,
    };

    this.openUpsertDialog(dialogData, (payload) => this.createProduct(payload));
  }

  onEditProduct(product: Product): void {
    if (this.isBusy()) {
      return;
    }

    const dialogData: ProductUpsertDialogData = {
      mode: 'edit',
      title: 'Editar produto',
      subtitle: 'Atualize os dados do produto.',
      initialValue: {
        nome: product.nome,
        marca: product.marca,
        valor: product.valor,
      },
    };

    this.openUpsertDialog(dialogData, (payload) => this.updateProduct(product.id, payload));
  }

  onRequestDelete(product: Product): void {
    if (this.isBusy()) {
      return;
    }

    const dialogData: ConfirmDeleteDialogData = { productName: product.nome };
    const dialogRef = this.dialog.open(ConfirmDeleteDialogComponent, {
      width: '360px',
      maxWidth: 'calc(100vw - 2rem)',
      disableClose: true,
      data: dialogData,
    });

    dialogRef
      .afterClosed()
      .pipe(take(1))
      .subscribe((shouldDelete: boolean) => {
        if (!shouldDelete) {
          return;
        }
        this.deleteProduct(product);
      });
  }

  onPageChange(change: ProductsPageChange): void {
    if (this.isBusy() || this.queryState().isLoading || this.queryState().isPolling) {
      return;
    }

    this.stopPolling();
    this.fetchProducts(
      {
        offset: change.offset,
        limit: change.limit,
      },
      true,
    );
  }

  private openUpsertDialog(
    data: ProductUpsertDialogData,
    onConfirm: (payload: ProductUpsertPayload) => void,
  ): void {
    const dialogRef = this.dialog.open(ProductUpsertDialogComponent, {
      width: '560px',
      maxWidth: 'calc(100vw - 2rem)',
      disableClose: true,
      data,
    });

    dialogRef
      .afterClosed()
      .pipe(take(1))
      .subscribe((payload: ProductUpsertPayload | undefined) => {
        if (!payload) {
          return;
        }

        const normalizedPayload = this.normalizePayload(payload);
        if (!normalizedPayload) {
          this.toast.error('Preencha os campos corretamente.');
          return;
        }

        onConfirm(normalizedPayload);
      });
  }

  private fetchProducts(query: ProductsListQuery, showLoadingState: boolean): void {
    if (showLoadingState) {
      this.patchQueryState({ isLoading: true });
    }

    this.productsApiService
      .listProducts(query)
      .pipe(
        take(1),
        finalize(() => {
          if (showLoadingState) {
            this.patchQueryState({ isLoading: false });
          }
        }),
      )
      .subscribe({
        next: (response) => {
          const normalizedOffset = this.normalizeOffset(
            response.total,
            response.offset,
            response.limit,
          );

          if (normalizedOffset !== response.offset) {
            this.patchPagination({
              offset: normalizedOffset,
              limit: response.limit,
              total: response.total,
            });
            this.fetchProducts(
              {
                offset: normalizedOffset,
                limit: response.limit,
              },
              false,
            );
            return;
          }

          this.products.set(response.items);
          this.patchPagination({
            offset: response.offset,
            limit: response.limit,
            total: response.total,
          });
          this.patchQueryState({ errorMessage: null });
        },
        error: (error: unknown) => {
          this.handleProductsError(error, 'load');
        },
      });
  }

  private createProduct(payload: ProductUpsertPayload): void {
    const previousTotal = this.pagination().total;
    this.isSaving.set(true);

    this.productsApiService
      .createProduct(payload)
      .pipe(
        take(1),
        finalize(() => this.isSaving.set(false)),
      )
      .subscribe({
        next: () => {
          this.toast.info('Solicitacao de criacao enviada. Atualizando lista...');
          this.startPolling({
            operation: 'create',
            previousTotal,
            query: this.currentQuery(),
            payload,
          });
        },
        error: (error: unknown) => {
          this.handleProductsError(error, 'create');
        },
      });
  }

  private updateProduct(productId: number, payload: ProductUpsertPayload): void {
    const previousTotal = this.pagination().total;
    this.isSaving.set(true);

    this.productsApiService
      .updateProduct(productId, payload)
      .pipe(
        take(1),
        finalize(() => this.isSaving.set(false)),
      )
      .subscribe({
        next: () => {
          this.toast.info('Solicitacao de atualizacao enviada. Atualizando lista...');
          this.startPolling({
            operation: 'update',
            previousTotal,
            query: this.currentQuery(),
            productId,
            payload,
          });
        },
        error: (error: unknown) => {
          this.handleProductsError(error, 'update');
        },
      });
  }

  private deleteProduct(product: Product): void {
    const previousTotal = this.pagination().total;
    this.deletingProductId.set(product.id);

    this.productsApiService
      .deleteProduct(product.id)
      .pipe(
        take(1),
        finalize(() => this.deletingProductId.set(null)),
      )
      .subscribe({
        next: () => {
          this.toast.info('Solicitacao de exclusao enviada. Atualizando lista...');
          this.startPolling({
            operation: 'delete',
            previousTotal,
            query: this.currentQuery(),
            productId: product.id,
          });
        },
        error: (error: unknown) => {
          this.handleProductsError(error, 'delete');
        },
      });
  }

  private startPolling(expectation: PollExpectation): void {
    this.stopPolling();
    this.patchQueryState({ isPolling: true, errorMessage: null });

    let attempts = 0;
    this.pollingSubscription = timer(0, POLL_INTERVAL_MS)
      .pipe(switchMap(() => this.productsApiService.listProducts(expectation.query)))
      .subscribe({
        next: (response) => {
          attempts += 1;

          const normalizedOffset = this.normalizeOffset(
            response.total,
            response.offset,
            response.limit,
          );
          if (normalizedOffset !== response.offset) {
            expectation.query = {
              offset: normalizedOffset,
              limit: response.limit,
            };
            this.patchPagination({
              offset: normalizedOffset,
              limit: response.limit,
              total: response.total,
            });
            return;
          }

          this.products.set(response.items);
          this.patchPagination({
            offset: response.offset,
            limit: response.limit,
            total: response.total,
          });

          if (this.isExpectationSatisfied(expectation, response)) {
            this.stopPolling();
            return;
          }

          if (attempts >= POLL_MAX_ATTEMPTS) {
            this.stopPolling();
            this.toast.info(
              'Operacao em processamento. Atualize novamente em alguns segundos.',
            );
          }
        },
        error: (error: unknown) => {
          this.stopPolling();
          this.handleProductsError(error, 'load');
        },
      });
  }

  private stopPolling(): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = null;
    }
    this.patchQueryState({ isPolling: false });
  }

  private isExpectationSatisfied(
    expectation: PollExpectation,
    response: ProductsListResponse,
  ): boolean {
    if (expectation.operation === 'create') {
      return response.total > expectation.previousTotal;
    }

    if (expectation.operation === 'delete') {
      return response.total < expectation.previousTotal;
    }

    if (expectation.productId === undefined || !expectation.payload) {
      return false;
    }

    const currentProduct = response.items.find((product) => product.id === expectation.productId);
    if (!currentProduct) {
      return false;
    }

    return this.isProductMatchingPayload(currentProduct, expectation.payload);
  }

  private normalizeOffset(total: number, offset: number, limit: number): number {
    if (total <= 0) {
      return 0;
    }

    if (offset < total) {
      return offset;
    }

    return Math.floor((total - 1) / limit) * limit;
  }

  private isProductMatchingPayload(product: Product, payload: ProductUpsertPayload): boolean {
    return (
      product.nome.trim().toLowerCase() === payload.nome.trim().toLowerCase() &&
      product.marca.trim().toLowerCase() === payload.marca.trim().toLowerCase() &&
      Math.abs(product.valor - payload.valor) < 0.005
    );
  }

  private currentQuery(): ProductsListQuery {
    const pagination = this.pagination();
    return {
      offset: pagination.offset,
      limit: pagination.limit,
    };
  }

  private handleProductsError(error: unknown, operation: ProductOperationType | 'load'): void {
    if (error instanceof RxTimeoutError) {
      this.showOperationError(operation, 'Servidor demorou para responder. Tente novamente.');
      return;
    }

    if (!(error instanceof HttpErrorResponse)) {
      this.showOperationError(operation, this.getGenericErrorMessage(operation));
      return;
    }

    if (this.handleAuthenticationError(error)) {
      return;
    }

    const apiError = this.readApiError(error);
    if (error.status === 404 && apiError === 'product_not_found') {
      this.toast.info('Produto nao encontrado. A lista sera atualizada.');
      this.fetchProducts(this.currentQuery(), false);
      return;
    }

    const validationMessage = this.mapApiErrorMessage(apiError);
    if (validationMessage) {
      this.showOperationError(operation, validationMessage);
      return;
    }

    this.showOperationError(operation, this.getGenericErrorMessage(operation));
  }

  private handleAuthenticationError(error: HttpErrorResponse): boolean {
    if (error.status !== 401) {
      return false;
    }

    const apiError = this.readApiError(error);
    if (
      apiError !== 'missing_token' &&
      apiError !== 'invalid_token' &&
      apiError !== 'expired_token' &&
      apiError !== null
    ) {
      return false;
    }

    this.stopPolling();
    this.authService.clearSession();
    this.toast.error('Sessao expirada. Faca login novamente.');
    void this.router.navigate(['/login'], {
      queryParams: { redirect: '/products' },
    });
    return true;
  }

  private showOperationError(operation: ProductOperationType | 'load', message: string): void {
    if (operation === 'load') {
      this.patchQueryState({ errorMessage: message });
    }
    this.toast.error(message);
  }

  private getGenericErrorMessage(operation: ProductOperationType | 'load'): string {
    if (operation === 'create') {
      return 'Nao foi possivel salvar o produto agora.';
    }
    if (operation === 'update') {
      return 'Nao foi possivel atualizar o produto agora.';
    }
    if (operation === 'delete') {
      return 'Nao foi possivel excluir o produto agora.';
    }
    return 'Nao foi possivel carregar a lista de produtos.';
  }

  private mapApiErrorMessage(apiError: string | null): string | null {
    if (apiError === null) {
      return null;
    }

    if (apiError === 'invalid_payload') {
      return 'Dados invalidos. Verifique os campos.';
    }
    if (apiError === 'nome_is_required' || apiError === 'nome_must_be_string') {
      return 'Informe o nome do produto.';
    }
    if (apiError === 'marca_is_required' || apiError === 'marca_must_be_string') {
      return 'Informe a marca do produto.';
    }
    if (apiError === 'valor_must_be_numeric') {
      return 'Informe um valor numerico valido.';
    }
    if (apiError === 'valor_must_be_greater_than_zero') {
      return 'Informe um valor maior que zero.';
    }
    if (apiError === 'offset_must_be_non_negative_integer') {
      return 'Parametro de paginacao offset invalido.';
    }
    if (apiError === 'limit_must_be_positive_integer') {
      return 'Parametro de paginacao limit invalido.';
    }

    return null;
  }

  private normalizePayload(payload: ProductUpsertPayload): ProductUpsertPayload | null {
    const nome = payload.nome.trim();
    const marca = payload.marca.trim();
    const valor = Number(payload.valor);

    if (!nome || !marca || !Number.isFinite(valor) || valor <= 0) {
      return null;
    }

    return {
      nome,
      marca,
      valor: Number(valor.toFixed(2)),
    };
  }

  private patchQueryState(partial: Partial<ProductsQueryState>): void {
    this.queryState.update((currentState) => ({
      ...currentState,
      ...partial,
    }));
  }

  private patchPagination(partial: Partial<PaginationState>): void {
    this.pagination.update((currentState) => ({
      ...currentState,
      ...partial,
    }));
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
