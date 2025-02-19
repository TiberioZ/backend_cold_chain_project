from pydantic import BaseModel, Field


class FoodRequest(BaseModel):
    barcode: str = Field(
        ...,
        title="The barcode of the food item",
        example="123456789",
    )
    capteurID: str = Field(
        ...,
        title="The ID of the temperature sensor",
        example="FRIDGE_001",
    )


class TemparatureRequest(BaseModel):
    captorId: str = Field(
        ...,
        title="The captorId of the temperature reading",
        example="FRIDGE_001",
    )
    temperature: float = Field(
        ...,
        title="The temperature of the food item",
        example=4.5,
    )
    timestamp: str = Field(
        ...,
        title="The timestamp of the temperature reading",
        example="2024-03-19 15:30:00",
    )
