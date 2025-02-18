from pydantic import BaseModel, Field


class FoodRequest(BaseModel):
    barcode: str = Field(
        ...,
        title="The barcode of the food item",
        example="123456789",
    )
    temperature: float = Field(
        ...,
        title="The temperature of the food item",
        example=4.5,
    )
