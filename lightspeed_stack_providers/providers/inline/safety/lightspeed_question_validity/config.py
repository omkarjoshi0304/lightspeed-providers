from typing import Any

from pydantic import BaseModel, Field


class QuestionValidityShieldConfig(BaseModel):
    model_id: str | None = Field(
        default=None,
        description="The model_id to use for the guard",
    )

    @classmethod
    def sample_run_config(
        cls, model_id: str = "${env.INFERENCE_MODEL}", **kwargs
    ) -> dict[str, Any]:
        return {
            "model_id": model_id,
        }
