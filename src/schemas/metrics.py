from pydantic import BaseModel

class MetricsResponse(BaseModel):
    churn_ratio: float
    weekend_commit_ratio: float
    pr_turnaround_hours: float
    review_latency_hours: float
    workflow_type: str

    class Config:
        from_attributes = True
