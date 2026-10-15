
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SyncPad</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 0 20px;
            }

            #status {
                color: green;
            }

            textarea {
                width: 100%;
                height: 400px;
                padding: 12px;
                box-sizing: border-box;
                font: 16px monospace;
                resize: vertical;
            }
        </style>
    </head>
    <body>
        <h1>SyncPad</h1>
        <p id="status">Connecting...</p>

        <textarea id="editor"
            placeholder="Start typing here..."></textarea>

        <script>
            const ws = new WebSocket(
                `ws://${location.host}/ws`
            );

            const editor = document.getElementById("editor");
            const status = document.getElementById("status");

            ws.onopen = () => {
                status.textContent = "Connected";
            };

            ws.onmessage = (event) => {
                if (editor.value !== event.data) {
                    const start = editor.selectionStart;
                    const end = editor.selectionEnd;

                    editor.value = event.data;

                    editor.setSelectionRange(
                        Math.min(start, editor.value.length),
                        Math.min(end, editor.value.length)
                    );
                }
            };

            ws.onclose = () => {
                status.textContent = "Disconnected";
            };

            ws.onerror = () => {
                status.textContent = "Connection error";
            };

            editor.addEventListener("input", () => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(editor.value);
                }
            });
        </script>
    </body>
    </html>
    """)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
