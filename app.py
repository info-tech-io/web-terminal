import asyncio
import fcntl
import os
import pty
import struct
import termios

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

ROOT = os.environ.get("ROOT_PATH", "")  # e.g. "/claude" when behind nginx subpath

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

WEB_TOKEN = os.environ["WEB_TOKEN"]


@app.get("/login")
async def login_page():
    with open("templates/login.html") as f:
        return HTMLResponse(f.read())


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    if form.get("token") == WEB_TOKEN:
        response = RedirectResponse(f"{ROOT}/", status_code=302)
        response.set_cookie("auth_token", WEB_TOKEN, httponly=True, samesite="strict", secure=True)
        return response
    return RedirectResponse(f"{ROOT}/login?error=1", status_code=302)


@app.get("/")
async def index(request: Request):
    if request.cookies.get("auth_token") != WEB_TOKEN:
        return RedirectResponse(f"{ROOT}/login")
    with open("templates/index.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def terminal(ws: WebSocket):
    token = ws.cookies.get("auth_token") or ws.query_params.get("token")
    if token != WEB_TOKEN:
        await ws.close(code=4401)
        return
    await ws.accept()

    master_fd, slave_fd = pty.openpty()
    # Match the tmux session's initial dimensions so attach doesn't shrink it
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ,
                struct.pack("HHHH", 60, 220, 0, 0))
    proc = await asyncio.create_subprocess_exec(
        "tmux", "attach-session", "-t", "main",
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        close_fds=True,
    )
    os.close(slave_fd)

    async def read_from_pty():
        loop = asyncio.get_running_loop()
        while True:
            try:
                data = await loop.run_in_executor(None, os.read, master_fd, 4096)
                await ws.send_bytes(data)
            except OSError:
                break

    async def write_to_pty():
        while True:
            try:
                msg = await ws.receive()
                if "bytes" in msg:
                    data = msg["bytes"]
                    if len(data) == 5 and data[0] == 0x01:
                        rows = int.from_bytes(data[1:3], "big")
                        cols = int.from_bytes(data[3:5], "big")
                        fcntl.ioctl(master_fd, termios.TIOCSWINSZ,
                                    struct.pack("HHHH", rows, cols, 0, 0))
                    else:
                        os.write(master_fd, data)
                elif "text" in msg:
                    os.write(master_fd, msg["text"].encode())
            except WebSocketDisconnect:
                break

    try:
        await asyncio.gather(read_from_pty(), write_to_pty())
    finally:
        proc.terminate()
        try:
            os.close(master_fd)
        except OSError:
            pass
