
from pydantic import BaseModel, ConfigDict, Field


class PatientRecordLookupInput(BaseModel):
    """Input contract for read-only HMIS patient lookup."""

    model_config = ConfigDict(extra="forbid")

    patient_id: str = Field(
        min_length=1,
        max_length=100,
        description="Unique patient identifier from the hospital HMIS.",
    )


