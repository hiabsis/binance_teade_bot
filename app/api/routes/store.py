from fastapi import APIRouter, Body

from app.model.schemas.store import BoolResponse, StartTestStoreRequest

router = APIRouter()


@router.post("/test/strategy", response_model=BoolResponse, name="test:strategy")
def test_strategy(
        user_login: StartTestStoreRequest = Body(..., ),

) -> BoolResponse:
    # StoreClient.run(strategy=StoreStrategy)
    return BoolResponse(
        status=True,
        message="test_strategy"
    )
