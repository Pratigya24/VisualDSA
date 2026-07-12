from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_topic_service
from app.models.user import User
from app.schemas.topic import TopicListResponse, TopicResponse
from app.services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=TopicListResponse)
async def list_topics(
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
) -> TopicListResponse:
    topics = await topic_service.list_roadmap(current_user.id)
    return TopicListResponse(topics=topics)


@router.get("/{slug}", response_model=TopicResponse)
async def get_topic(
    slug: str,
    current_user: Annotated[User, Depends(get_current_user)],
    topic_service: Annotated[TopicService, Depends(get_topic_service)],
) -> TopicResponse:
    return await topic_service.get_topic_detail(slug, current_user.id)
