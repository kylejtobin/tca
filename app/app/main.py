from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI(title="TCA")


class HealthStatus(BaseModel):
    model_config = ConfigDict(frozen=True)
    status: Literal["ok"] = "ok"


@app.get("/health")
async def health() -> HealthStatus:
    return HealthStatus()
