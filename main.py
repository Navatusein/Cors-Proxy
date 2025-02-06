import logging
import httpx
import uvicorn
import socket

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from config import Settings

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

settings = Settings()

origins = settings.origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/work", methods=["GET"])
async def work():
    return JSONResponse(content="I am alive!", status_code=200)


@app.api_route("/tcp", methods=["POST"])
async def tcp(request: Request):
    try:
        target_address = request.query_params.get("address")
        target_port = int(request.query_params.get("port"))

        content = await request.body()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((target_address, target_port))
            client.sendall(content)
            response = client.recv(1024).decode()
            return JSONResponse(content=response, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.api_route("/proxy", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(request: Request):
    target_url = request.query_params.get("url")
    if not target_url:
        return {"error": "Parameter 'url' is required"}, 400

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={key: value for key, value in request.headers.items() if key != "host"},
                content=await request.body(),
            )

            expose_headers = list(response.headers.keys())

            return JSONResponse(
                content=response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
                status_code=200 if 300 <= response.status_code < 400 else response.status_code,
                headers={
                    **dict(response.headers),
                    "Access-Control-Expose-Headers": ", ".join(expose_headers),
                },
            )
        except Exception as e:
            return JSONResponse(content= {"error": str(e)}, status_code=500)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")