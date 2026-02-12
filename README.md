# Desafio Tecnico

## 1) Subir tudo com Docker Compose

```terminal
Copy-Item backend/.env.example backend/.env
docker compose up --build
```

URLs:

- Frontend: `http://localhost:4200`
- API: `http://localhost:5000`
- Swagger: `http://localhost:5000/docs`

## 2) Rodar testes via Docker

Sobe apenas banco e redis para os testes:

```terminal
docker compose up -d db redis
```

Executa testes unitarios do backend:

```terminal
docker compose run --rm api pytest -q tests/unit
```

Executa testes de integracao do backend:

```terminal
docker compose run --rm api pytest -q tests/integration
```
