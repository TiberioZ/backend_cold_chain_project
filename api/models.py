from pydantic import BaseModel, Field


class FoodRequest(BaseModel):
    barcode: str = Field(
        ...,
        title="The barcode of the food item",
        example="123456789",
    )


class TemparatureRequest(BaseModel):
    temperature: float = Field(
        ...,
        title="The temperature of the food item",
        example=4.5,
    )
    timestamp: str = Field(
        ...,
        title="The timestamp of the temperature reading",
        examples=["710222002"],
    )
