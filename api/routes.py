from fastapi import APIRouter

from api.models import FoodRequest, TemparatureRequest
from api.services import ColdChainService


cold_chain_router = APIRouter()
service = ColdChainService()


@cold_chain_router.post("/temperature")
async def post_temperature(request: TemparatureRequest):
    return service.post_temperature(request.temperature, request.timestamp)


@cold_chain_router.get("/food")
async def get_food_advise(request: FoodRequest):
    return service.get_advise_for_food_item(request.barcode, request.temperature)
