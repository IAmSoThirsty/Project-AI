from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time

router = APIRouter(prefix="/vr", tags=["VR"])

class VRCommand(BaseModel):
    type: str
    params: Dict[str, Any]
    timestamp: float = time.time()

# Simple in-memory queue for demo purposes
# In production, use Redis or similar
command_queue: List[VRCommand] = []

@router.post("/command")
def send_command(cmd: VRCommand):
    """Send a command to the VR system"""
    command_queue.append(cmd)
    # Keep queue size manageable
    if len(command_queue) > 100:
        command_queue.pop(0)
    return {"status": "queued", "queue_size": len(command_queue)}

@router.get("/commands")
def get_commands(since: float = 0):
    """Poll for new commands (VR Client calls this)"""
    return [c for c in command_queue if c.timestamp > since]
