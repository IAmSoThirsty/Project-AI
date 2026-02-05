"""
Save Points API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from project_ai.save_points import SavePointsManager, get_auto_save_service

router = APIRouter(prefix="/api/savepoints", tags=["savepoints"])
save_manager = SavePointsManager()


class CreateSaveRequest(BaseModel):
    name: str
    metadata: Optional[Dict] = None


class RestoreRequest(BaseModel):
    save_id: str


@router.post("/create")
async def create_save_point(request: CreateSaveRequest):
    """Create a user save point"""
    try:
        result = save_manager.create_user_save(request.name, request.metadata)
        return {"success": True, "save_point": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_save_points():
    """List all save points (user and auto)"""
    try:
        return save_manager.list_save_points()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore/{save_id}")
async def restore_save_point(save_id: str):
    """Restore from a save point"""
    try:
        success = save_manager.restore_save_point(save_id)
        if not success:
            raise HTTPException(status_code=404, detail="Save point not found")
        return {"success": True, "message": f"Restored to save point: {save_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{save_id}")
async def delete_save_point(save_id: str):
    """Delete a user save point"""
    try:
        success = save_manager.delete_save_point(save_id)
        if not success:
            raise HTTPException(status_code=404, detail="Save point not found or cannot be deleted")
        return {"success": True, "message": f"Deleted save point: {save_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto/status")
async def auto_save_status():
    """Get auto-save service status"""
    try:
        auto_service = get_auto_save_service()
        return auto_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialize auto-save service on module load
async def start_auto_save():
    """Start auto-save background service"""
    auto_service = get_auto_save_service()
    await auto_service.start()


async def stop_auto_save():
    """Stop auto-save background service"""
    auto_service = get_auto_save_service()
    await auto_service.stop()
