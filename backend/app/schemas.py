from pydantic import BaseModel, Field
from typing import Optional

class WaferInput(BaseModel):
    temperature_c: float
    pressure_torr: float
    gas_flow_sccm: float
    etch_rate_nm_min: float
    voltage_v: float
    current_ma: float
    process_step: str

class PredictionRequest(WaferInput):
    sample_id: Optional[str] = None

class WhatIfRequest(WaferInput):
    modified_parameter: str
    modified_value: float

class FeedbackRequest(BaseModel):
    prediction_id: int
    actual_label: str
    confirmed_root_cause: Optional[str] = None
    prediction_correct: bool
    engineer_comment: Optional[str] = ''

class RetrainRequest(BaseModel):
    confirm: bool = Field(default=False)
