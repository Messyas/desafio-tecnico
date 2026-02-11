# Desafio Tecnico - Bootstrap de Ambiente

Este repositório está no milestone de **configuração base de ambiente** para iniciar o desenvolvimento com TDD.

## Objetivo desta fase

- Backend Flask com PostgreSQL local (Docker) pronto para evoluir.
- Redis e worker separados no Docker Compose.
- Endpoints de saúde com separação de liveness/readiness.
- Base de testes unitários no backend.
- CI no GitHub Actions para backend.

## O que ainda não está implementado

- Login/JWT e proteção de rotas.
- CRUD completo de produtos.
- Processamento de fila de negócio no worker.
- CD/deploy automático.

## Como subir o ambiente

### 1) Compose padrão (Postgres local + Redis + API + Worker + Frontend)

```bash
docker compose up --build
```

## Rodar testes do backend

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Endpoints de saúde

- `GET /health` -> liveness (sempre 200 enquanto processo estiver vivo)
- `GET /healthz` -> alias de compatibilidade de `GET /health`
- `GET /ready` -> readiness (200 quando DB + Redis estão OK, 503 caso contrário)

## Variáveis de ambiente essenciais (backend)

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@db:5432/desafio` | URL do PostgreSQL local |
| `REDIS_URL` | `redis://redis:6379/0` | URL do Redis |
| `REDIS_REQUIRED` | `false` | `true` para fail-fast no startup |
| `READINESS_REDIS_TIMEOUT_MS` | `250` | Timeout do check de Redis |
| `READINESS_DB_TIMEOUT_MS` | `1000` | Timeout/configuração do check de DB |

## CI

- Workflow: `.github/workflows/backend-ci.yml`
- Executa em `push`/`pull_request` com mudanças em `backend/**`.
- Instala dependências do backend e roda `pytest`.
