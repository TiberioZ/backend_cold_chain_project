from fastapi import FastAPI
import uvicorn
from api.routes import cold_chain_router


app = FastAPI(
    title="cold chain api",
    version="1.0.0",
)

app.include_router(cold_chain_router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
