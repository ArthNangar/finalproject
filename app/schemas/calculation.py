from pydantic import BaseModel, Field


class CalcIn(BaseModel):
    op: str = Field(description="add/sub/mul/div/mod/pow")
    a: float
    b: float


class ExpressionIn(BaseModel):
    expression: str = Field(min_length=1, description="Math expression like (5+3)*2")


class CalcOut(BaseModel):
    id: int
    op: str
    a: float
    b: float
    expression: str | None = None
    result: float

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    total_calculations: int
    average_result: float
    last_operation: str | None
