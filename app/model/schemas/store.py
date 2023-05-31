from app.model.deomain.rwmodel import RWModel


class BoolResponse(RWModel):
    message: str = ""
    status: bool = True


class StartTestStoreRequest(RWModel):
    symbol: str = "OPUSDT"
    timeframe: str = "1m"
