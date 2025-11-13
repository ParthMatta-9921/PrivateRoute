from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, departments, roles, communication_rules, messages, audit

app = FastAPI(
    title="PrivateRoute API",
    description="Backend API for PrivateRoute - Inter-Departmental Communication Management System",
    version="1.0.0"
)


@app.on_event("startup")
async def create_tables():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(roles.router)
app.include_router(communication_rules.router)
app.include_router(messages.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {
        "message": "PrivateRoute API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

