import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from LLM import handle_response, memory, prompt
import yaml
import bcrypt
from langchain.schema import HumanMessage
import asyncio

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)

def load_credentials():
    with open("config_users1.yml", "r") as file:
        config = yaml.safe_load(file)
        return config["credentials"]

credentials = load_credentials()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = {"history": "", "buffer": ""}
        logging.info(f"WebSocket connected: {websocket.client}")


    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            logging.info(f"WebSocket disconnected: {websocket.client}")


    async def send_message(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            self.disconnect(websocket)

    async def send_buffered_message(self, websocket: WebSocket):
        """Send the buffered message if the buffer is not empty."""
        if websocket in self.active_connections:
            buffer = self.active_connections[websocket].get("buffer", "")
            if buffer:
                await self.send_message(websocket, buffer)
                self.active_connections[websocket]["buffer"] = ""  # Clear the buffer

    
    def get_history(self, websocket: WebSocket):
        return self.active_connections.get(websocket, {}).get("history", "")

    def update_history(self, websocket: WebSocket, user_input: str, bot_response: str):
        if websocket in self.active_connections:
            history = self.active_connections[websocket]["history"]
            updated_history = f"{history}\nUser: {user_input}\nAssistant: {bot_response}"
            self.active_connections[websocket]["history"] = updated_history
            
    def reset_buffer(self, websocket: WebSocket):
        """Reset the temporary buffer for the current response."""
        if websocket in self.active_connections:
            self.active_connections[websocket]["buffer"] = ""

manager = ConnectionManager()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/validate_login")
async def validate_login(data: LoginRequest):
    for user in credentials:
        if data.username == user["username"]:
            if bcrypt.checkpw(data.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/", response_class=HTMLResponse)
async def serve_html():
    try:
        with open("interface-stream.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            # Receive user input
            data = await websocket.receive_text()
            logging.debug(f"[WebSocket] Received message from client: {data}")

            # Retrieve conversation history
            history = manager.get_history(websocket)

            # Build the prompt for the model
            formatted_prompt = prompt.format(
                history=history,
                query=data
            )

            inputs = {
                "query": data,
                "formatted_prompt": formatted_prompt
            }

            try:
                # Process the response (streaming or non-streaming)
                response = await handle_response(inputs)
                accumulated_text = ""  # Reset the buffer for this response

                if hasattr(response, '__aiter__'):  # Streaming response
                    async for chunk in response:
                        content = chunk.get("content", "") if isinstance(chunk, dict) else chunk
                        if content:
                            # Accumulate the current response chunk
                            accumulated_text += content

                            # Store the chunk in the buffer (optional for retries)
                            manager.active_connections[websocket]["buffer"] += content

                            # Send the new chunk to the client
                            await manager.send_message(websocket, content)

                    # Update the full conversation history
                    manager.update_history(websocket, data, accumulated_text)

                else:  # Non-streaming response
                    bot_response = response.get("response", "Error: No response generated")
                    await manager.send_message(websocket, bot_response)
                    manager.update_history(websocket, data, bot_response)

            except Exception as e:
                error_message = f"Error processing query: {e}"
                logging.error(f"[WebSocket] {error_message}")
                await manager.send_message(websocket, error_message)

    except WebSocketDisconnect:
        logging.info(f"[WebSocket] Client disconnected: {websocket.client}")
        manager.disconnect(websocket)
