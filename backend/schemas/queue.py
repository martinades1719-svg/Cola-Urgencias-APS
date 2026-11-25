from pydantic import BaseModel

from schemas.episode import EpisodeResponse


class WaitEstimateResponse(BaseModel):
    min: int
    max: int
    available: bool


class QueuePositionResponse(BaseModel):
    approximate: int | None
    estimate: WaitEstimateResponse
    reordered: bool


class QueueItemResponse(EpisodeResponse):
    position: int
    estimate: WaitEstimateResponse
    hasAlert: bool = False


class QueueListDataResponse(BaseModel):
    data: list[QueueItemResponse]


class QueuePositionDataResponse(BaseModel):
    data: QueuePositionResponse