from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import (
    ChatServiceError,
    process_chat,
)


router = APIRouter(
    prefix="/sessions",
    tags=["chat"],
)


@router.post(
    "/{session_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    session_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        return process_chat(
            db=db,
            session_id=session_id,
            message=payload.message,
            agent=payload.agent,
        )

    except ChatServiceError as exc:
        if str(exc) == "Session not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
