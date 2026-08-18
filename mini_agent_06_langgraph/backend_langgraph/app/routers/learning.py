from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.workflows.learning_graphs import (
    compare_workflows, graph_components, run_branch, run_checkpoint, run_loop,
)


learning_router = APIRouter(prefix="/api/learning/graph", tags=["Beginner Graph"])


class BranchRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class LoopRequest(BaseModel):
    budget: int = Field(gt=0)
    max_iterations: int = Field(default=1, ge=0, le=5)


class ThreadRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)


@learning_router.get("/components")
def components() -> dict:
    return graph_components()


@learning_router.post("/branch")
def branch(payload: BranchRequest) -> dict:
    return run_branch(payload.message)


@learning_router.post("/loop")
def loop(payload: LoopRequest) -> dict:
    return run_loop(payload.budget, payload.max_iterations)


@learning_router.post("/checkpoint")
def checkpoint(payload: ThreadRequest) -> dict:
    return run_checkpoint(payload.thread_id)


@learning_router.post("/compare")
def compare(payload: BranchRequest) -> dict:
    return compare_workflows(payload.message)
