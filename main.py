
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SyncCode - WebSocket Test</title>
    </head>
    <body>
        <h1>SyncCode WebSocket Test</h1>
        <p id="status">Connecting...</p>

        <input id="message" placeholder="Enter a message">
        <button onclick="sendMessage()">Send</button>

        <h3>Messages</h3>
        <ul id="messages"></ul>

        <script>
            const ws = new WebSocket(
                `ws://${location.host}/ws`
            );

            const status = document.getElementById("status");
            const messages = document.getElementById("messages");

            ws.onopen = () => {
                status.textContent = "Connected!";
            };

            ws.onmessage = (event) => {
                const li = document.createElement("li");
                li.textContent = event.data;
                messages.appendChild(li);
            };

            ws.onclose = () => {
                status.textContent = "Disconnected";
            };

            ws.onerror = () => {
                status.textContent = "Connection error";
            };

            function sendMessage() {
                const input = document.getElementById("message");

                if (ws.readyState === WebSocket.OPEN && input.value) {
                    ws.send(input.value);
                    input.value = "";
                }
            }
        </script>
    </body>
    </html>
    """)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Server received: {message}")

    except WebSocketDisconnect:
        print("Client disconnected")
