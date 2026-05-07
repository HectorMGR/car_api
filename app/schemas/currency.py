from pydantic import BaseModel, ConfigDict


class CurrencyBase(BaseModel):
    code: str
    symbol: str


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyResponse(CurrencyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)