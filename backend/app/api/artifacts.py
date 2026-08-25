from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.artifact import ArtifactResponse
from app.services.artifact_service import (
    ArtifactServiceError,
    get_artifact,
)


router = APIRouter(
    prefix="/artifacts",
    tags=["artifacts"],
)


@router.get(
    "/{artifact_id}",
    response_model=ArtifactResponse,
    status_code=status.HTTP_200_OK,
)
def get_artifact_endpoint(
    artifact_id: UUID,
    session_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    try:
        artifact = get_artifact(
            db=db,
            artifact_id=artifact_id,
            session_id=session_id,
        )

        if artifact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Artifact not found.",
            )

        return artifact

    except ArtifactServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
