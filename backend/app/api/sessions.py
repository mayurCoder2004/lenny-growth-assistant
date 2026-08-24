from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.sessions import (
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionResponse,
)
from app.services.session_service import (
    add_message,
    create_session,
    get_messages,
    get_session,
    get_sessions,
    get_user,
)


router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
):
    user = get_user(db, payload.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return create_session(
        db=db,
        user_id=payload.user_id,
        title=payload.title,
    )


@router.get(
    "/user/{user_id}",
    response_model=list[SessionResponse],
)
def list_user_sessions(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return get_sessions(
        db=db,
        user_id=user_id,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def get_chat_session(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    session_id: UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return add_message(
        db=db,
        session_id=session_id,
        role=payload.role,
        content=payload.content,
    )


@router.get(
    "/{session_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    session = get_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return get_messages(
        db=db,
        session_id=session_id,
    )
