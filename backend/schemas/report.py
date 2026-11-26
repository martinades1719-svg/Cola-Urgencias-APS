from pydantic import BaseModel, Field


class PriorityMetricResponse(BaseModel):
    priority: str
    count: int


class DashboardMetricsResponse(BaseModel):
    pending: int
    waiting: int
    called: int

    in_care: int = Field(
        alias="inCare",
    )

    alerts: int

    average_wait: int = Field(
        alias="averageWait",
    )

    registered: int

    arrival_triage: int = Field(
        alias="arrivalTriage",
    )

    triage_care: int = Field(
        alias="triageCare",
    )

    reassessments: int

    priority_changes: int = Field(
        alias="priorityChanges",
    )

    resolved_alerts: int = Field(
        alias="resolvedAlerts",
    )

    withdrawals: int

    estimate_accuracy: int = Field(
        alias="estimateAccuracy",
    )

    by_priority: list[PriorityMetricResponse] = Field(
        alias="byPriority",
    )

    model_config = {
        "populate_by_name": True,
    }


class DashboardDataResponse(BaseModel):
    data: DashboardMetricsResponse
