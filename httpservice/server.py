# server.py
import asyncio
import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "welcome.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

async def event_stream(message: str):
    for i in range(1, 4):
        yield f"Processing file {i}/3...\n"
        await asyncio.sleep(1)
    yield f"Here's the file content: {message}\n"

@app.get("/stream")
async def stream(message: str = "hello"):
    return StreamingResponse(event_stream(message), media_type="text/plain")

if __name__ == "__main__":
    # Start FastAPI app for classic HTTP streaming
    print("Starting FastAPI server for classic HTTP streaming...")
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)