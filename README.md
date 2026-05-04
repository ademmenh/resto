# Restaurant API

A Restaurant Api made by FastAPI Framework with Domain-Driven Design (DDD) architecture.

## Stack

- **Language**: Python 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Query Builder**: SQLAlchemy 2.0 + asyncpg
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Validation**: Pydantic v2
- **Reverse Proxy**: NGINX

## DDD Layer Convention (per module)

- `domain/` — entities, value objects, port interfaces, domain errors
- `application/` — use cases (one file per use case)
- `infrastructure/` — SQLAlchemy models, mappers, repository implementations
- `presentation/` — FastAPI routers, DTOs (request), RDTOs (response)

## Project Structure

```
src/
	auth/
		domain/
		application/
		infrastructure/
		presentation/
		tests/
	config/
	inventory/
	meals/
	sales/
	shared/
	users/
	app.py				# FastAPI app definition
	main.py				# Entry point
	main_dev.py			# Dev entry point

```

## API Documentation

| Method | Path                  | Access                                |
| ------ | --------------------- | ------------------------------------- |
| GET    | /api/v1/docs          | Public (Swagger UI)                   |
| GET    | /api/v1/redoc         | Public (ReDoc)                        |
| GET    | /api/v1/openapi.json  | Public                                |

## Environment Variables

- `DATABASE_URL` — PostgreSQL connection string
- `SESSION_SECRET` — Used as JWT signing secret
- `JWT_ALGORITHM` — Default: HS256
- `JWT_EXPIRY_DAYS` — Default: 7
- `DEBUG` — Default: false

## Running

### Development Environment

```bash
make build:dev
make start:dev
```

### Production Environment

```bash
make build:prod
make start:prod
```

## License

This project is licensed under the GPL v3 License.
