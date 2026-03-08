# ideaforge-microservice-auth (backend-forge)

This is a lightweight FastAPI service that acts as the primary Authentication Microservice for **PraxisForge**.

## Integration with PraxisForge
This service is responsible for handling user registration and login. Upon successful login, it issues a JWT (JSON Web Token) that is signed using the **same exact Secret Key** as PraxisForge.

PraxisForge is completely stateless regarding authentication and simply verifies that the JWT is signed with its secret string.

### Configuration
1. Make sure to share the `.env` variables between PraxisForge and this repository.
2. Specifically, ensure `JWT_SECRET` and `JWT_ALGORITHM` match exactly.

### Installation & Running (Docker)
The entire service is containerized for easy deployment alongside PraxisForge without port collisions.

```bash
# Build and start the services (postgres, minio, and the fastapi app)
docker-compose up --build -d
```

### Services & Ports
- **Auth API**: `http://localhost:8001` (Mapped from internal 8000)
- **PostgreSQL**: `localhost:15432` (Mapped from internal 5432)
- **MinIO**: `localhost:19000` (Mapped from internal 9000)

Make sure `PraxisForge` continues to run on `8000`. You can now access the Auth API docs at `http://localhost:8001/docs`.
