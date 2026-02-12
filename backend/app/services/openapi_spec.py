from __future__ import annotations


def build_openapi_spec() -> dict[str, object]:
    bearer_security = [{"bearerAuth": []}]

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Tech Home API",
            "version": "1.0.0",
            "description": "Api do sistema de cadastros de produtos.",
        },
        "paths": {
            "/ready": {
                "get": {
                    "summary": "Readiness check",
                    "responses": {
                        "200": {
                            "description": "Servico pronto",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ReadyResponse"}
                                }
                            },
                        },
                        "503": {
                            "description": "Dependencias indisponiveis",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ReadyResponse"}
                                }
                            },
                        },
                    },
                }
            },
            "/auth/register": {
                "post": {
                    "summary": "Criar conta de usuario",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AuthRegisterRequest"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Conta criada com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AuthTokenResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Payload invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "409": {
                            "description": "Conflito de email/nome",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
            "/auth/login": {
                "post": {
                    "summary": "Autenticar usuario",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AuthLoginRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Login com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AuthTokenResponse"}
                                }
                            },
                        },
                        "400": {
                            "description": "Payload invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Credenciais invalidas",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
            "/auth/logout": {
                "post": {
                    "summary": "Encerrar sessao",
                    "security": bearer_security,
                    "responses": {
                        "200": {
                            "description": "Logout com sucesso",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"status": {"type": "string"}},
                                        "required": ["status"],
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente/invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                }
            },
            "/products": {
                "get": {
                    "summary": "Listar produtos",
                    "security": bearer_security,
                    "parameters": [
                        {
                            "in": "query",
                            "name": "offset",
                            "required": False,
                            "schema": {"type": "integer", "minimum": 0, "default": 0},
                        },
                        {
                            "in": "query",
                            "name": "limit",
                            "required": False,
                            "schema": {"type": "integer", "minimum": 1},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Lista de produtos",
                            "headers": {
                                "X-Total-Count": {
                                    "schema": {"type": "integer", "minimum": 0}
                                },
                                "X-Offset": {
                                    "schema": {"type": "integer", "minimum": 0}
                                },
                                "X-Limit": {"schema": {"type": "integer", "minimum": 1}},
                            },
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Product"},
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Parametros de paginacao invalidos",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente/invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                },
                "post": {
                    "summary": "Enfileirar criacao de produto",
                    "security": bearer_security,
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ProductInput"}
                            }
                        },
                    },
                    "responses": {
                        "202": {
                            "description": "Operacao enfileirada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/QueuedOperationResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Payload invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente/invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                },
            },
            "/products/{product_id}": {
                "put": {
                    "summary": "Enfileirar atualizacao de produto",
                    "security": bearer_security,
                    "parameters": [
                        {
                            "in": "path",
                            "name": "product_id",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ProductInput"}
                            }
                        },
                    },
                    "responses": {
                        "202": {
                            "description": "Operacao enfileirada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/QueuedOperationResponse"
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Payload invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente/invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "404": {
                            "description": "Produto nao encontrado",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                },
                "delete": {
                    "summary": "Enfileirar exclusao de produto",
                    "security": bearer_security,
                    "parameters": [
                        {
                            "in": "path",
                            "name": "product_id",
                            "required": True,
                            "schema": {"type": "integer", "minimum": 1},
                        }
                    ],
                    "responses": {
                        "202": {
                            "description": "Operacao enfileirada",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/QueuedOperationResponse"
                                    }
                                }
                            },
                        },
                        "401": {
                            "description": "Token ausente/invalido",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                        "404": {
                            "description": "Produto nao encontrado",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                                }
                            },
                        },
                    },
                },
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                    },
                    "required": ["error"],
                },
                "AuthLoginRequest": {
                    "type": "object",
                    "properties": {
                        "identifier": {"type": "string"},
                        "password": {"type": "string"},
                    },
                    "required": ["identifier", "password"],
                },
                "AuthRegisterRequest": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string", "minLength": 8},
                    },
                    "required": ["name", "email", "password"],
                },
                "AuthTokenResponse": {
                    "type": "object",
                    "properties": {
                        "access_token": {"type": "string"},
                        "token_type": {"type": "string", "example": "Bearer"},
                        "expires_in": {"type": "integer", "minimum": 1},
                    },
                    "required": ["access_token", "token_type", "expires_in"],
                },
                "Product": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nome": {"type": "string"},
                        "marca": {"type": "string"},
                        "valor": {"type": "number"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                    },
                    "required": [
                        "id",
                        "nome",
                        "marca",
                        "valor",
                        "created_at",
                        "updated_at",
                    ],
                },
                "ProductInput": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "marca": {"type": "string"},
                        "valor": {"type": "number"},
                    },
                    "required": ["nome", "marca", "valor"],
                },
                "QueuedOperationResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "queued"},
                        "operation": {
                            "type": "string",
                            "enum": ["create", "update", "delete"],
                        },
                        "operation_id": {"type": "string"},
                        "product_id": {"type": "integer"},
                    },
                    "required": ["status", "operation", "operation_id"],
                },
                "ReadyCheck": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "duration_ms": {"type": "integer"},
                        "error": {"type": "string"},
                    },
                    "required": ["ok", "duration_ms"],
                },
                "ReadyResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "service": {"type": "string"},
                        "checks": {
                            "type": "object",
                            "properties": {
                                "database": {"$ref": "#/components/schemas/ReadyCheck"},
                                "redis": {"$ref": "#/components/schemas/ReadyCheck"},
                            },
                            "required": ["database", "redis"],
                        },
                        "time": {"type": "string", "format": "date-time"},
                    },
                    "required": ["status", "service", "checks", "time"],
                },
            },
        },
    }
