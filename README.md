# job-hunter


Automação pessoal para candidaturas de emprego usando IA - encontra vagas, gera currículos personalizados e automatiza aplicações.

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-hunter
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate  # On Windows
   
   pip install -e .
   ```

3. **Start PostgreSQL with Docker**
   ```bash
   docker compose -f docker/docker-compose.yml up postgres -d
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings if needed
   ```

5. **Run database migrations**
   ```bash
   ./migrate.sh upgrade
   ```

6. **Start the application**
   ```bash
   uvicorn src.profile.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Database Migrations

This project uses Alembic for database migrations. See [docs/MIGRATIONS.md](docs/MIGRATIONS.md) for detailed documentation.

### Quick Commands

```bash
# Create a new migration
./migrate.sh create "Description of changes"

# Apply pending migrations
./migrate.sh upgrade

# Rollback last migration
./migrate.sh downgrade

# View migration history
./migrate.sh history
```

## Project Structure

```
job-hunter/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── features/               # Feature modules
│   │   ├── user/              # User management
│   │   ├── profile/           # User profiles
│   │   ├── experience/        # Work experience
│   │   ├── education/         # Education history
│   │   ├── certificate/       # Certificates
│   │   ├── skill/             # Skills
│   │   ├── link/              # Social links
│   │   └── company/           # Company information
│   └── shared/                # Shared utilities
│       ├── database/          # Database configuration
│       └── exceptions/        # Exception handlers
├── alembic/                   # Database migrations
├── docker/                    # Docker configuration
└── docs/                      # Documentation
```

## Development

### Running Tests

```bash
# TODO: Add test commands
```

### API Documentation

When the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Services

### PostgreSQL

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up postgres -d

# Stop PostgreSQL
docker compose -f docker/docker-compose.yml down postgres

# View logs
docker compose -f docker/docker-compose.yml logs postgres

# Access PostgreSQL CLI
docker exec -it job_hunter_postgres psql -U user -d job_hunter
```

## License

GPL-3.0

## Author

Giovani Liskoski Zanini - giovanilzanini@gmail.com
