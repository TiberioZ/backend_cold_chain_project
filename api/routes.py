from fastapi import APIRouter
from typing import Optional

from api.models import FoodRequest, TemparatureRequest
from api.services import ColdChainService


cold_chain_router = APIRouter()
service = ColdChainService()


@cold_chain_router.post("/temperature")
async def post_temperature(request: TemparatureRequest):
    return await service.post_temperature(
        request.temperature, 
        request.timestamp,
        request.captorId
    )


@cold_chain_router.get("/food")
async def get_food_advise(barcode: str, capteurID: str):
    return await service.get_advise_for_food_item(barcode, capteurID)
