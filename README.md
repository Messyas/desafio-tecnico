# Desafio Tecnico - Flask + Redis + Angular

Aplicacao fullstack feita em:

- Backend em Flask
- Banco PostgreSQL
- Fila Redis e um Worker separado para processar as mensagens
- Frontend Angular

## Executar com Docker Compose 

1. Subir sistema completo:

```terminal
docker compose up --build
```

2. URLs:

- Frontend: `http://localhost:4200`
- API: `http://localhost:5000`
- DOCS: `http://localhost:5000/docs`

Migracoes:

- O servico `migrate` roda `flask --app app db upgrade` antes de `api` e `worker`.
- Para rodar migracao manualmente: `docker compose run --rm migrate`.

## Testes

### Backend

Com o Docker:

```terminal
docker compose up -d db redis
docker compose run --rm api pytest -q tests/unit
docker compose run --rm api pytest -q tests/integration
```