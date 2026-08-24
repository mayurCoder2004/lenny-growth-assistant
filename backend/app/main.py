from fastapi import FastAPI, HTTPException

from app.api.chat import router as chat_router
from app.api.sessions import router as sessions_router
from app.database import test_database_connection


app = FastAPI(
    title="The Lenny Growth Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "lenny-growth-assistant",
    }


@app.get("/health/database")
def database_health_check():
    try:
        test_database_connection()

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "unavailable",
                "message": str(exc),
            },
        )


app.include_router(sessions_router)
app.include_router(chat_router)
