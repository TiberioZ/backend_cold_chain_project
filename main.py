from fastapi import FastAPI
import uvicorn
from routes import cold_chain_router


app = FastAPI(
    title="cold chain api",
    version="1.0.0",
    swagger_ui_parameters={"docExpansion": "none"},
)

app.include_router(cold_chain_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
