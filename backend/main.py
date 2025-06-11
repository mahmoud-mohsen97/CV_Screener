"""
FastAPI server implementation for CV Screener.
Handles HTTP endpoints and background tasks.
"""

import os
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio

from .cv_screener import CVScreener

# Initialize FastAPI app
app = FastAPI(
    title="CV Screener API",
    description="AI-powered CV screening and analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store tasks and their status
tasks = {}

class JobRole(BaseModel):
    """Job role requirements model."""
    position: str
    must_have: List[str]
    nice_to_have: List[str]

class TaskStatus(BaseModel):
    """Task status response model."""
    task_id: str
    status: str
    progress: Dict
    result_path: Optional[str] = None
    error: Optional[str] = None

@app.post("/screen-cvs")
async def screen_cvs(
    zip_file: UploadFile,
    role: JobRole,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Start CV screening process.
    
    Args:
        zip_file: ZIP file containing CVs
        role: Job role requirements
        background_tasks: FastAPI background tasks
        
    Returns:
        Dict with task ID
    """
    try:
        # Validate file
        if not zip_file.filename.lower().endswith('.zip'):
            raise HTTPException(
                status_code=400,
                detail="Only ZIP files are accepted"
            )
            
        # Read file content
        content = await zip_file.read()
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        tasks[task_id] = {
            "status": "PROCESSING",
            "progress": {
                "processed": 0,
                "total": 0,
                "status": "Initializing",
                "percentage": 0
            },
            "result_path": None,
            "error": None
        }
        
        # Start background processing
        background_tasks.add_task(
            process_cvs_task,
            task_id,
            content,
            role
        )
        
        return {"task_id": task_id}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

async def process_cvs_task(
    task_id: str,
    zip_content: bytes,
    role: JobRole
):
    """Background task for CV processing."""
    try:
        # Initialize screener
        role_data = {
            "position": role.position,
            "requirements_must_have": role.must_have,
            "requirements_nice_to_have": role.nice_to_have
        }
        screener = CVScreener(role_data)
        
        # Process ZIP file
        result_path = await screener.process_zip(zip_content)
        
        # Update task status
        tasks[task_id].update({
            "status": "COMPLETED",
            "progress": screener.get_progress(),
            "result_path": result_path
        })
        
    except Exception as e:
        # Update task status with error
        tasks[task_id].update({
            "status": "FAILED",
            "error": str(e)
        })

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str) -> TaskStatus:
    """Get status of a processing task."""
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
        
    task = tasks[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result_path=task["result_path"],
        error=task["error"]
    )

@app.get("/download-result/{task_id}")
async def download_result(task_id: str) -> FileResponse:
    """Download the Excel report for a completed task."""
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
        
    task = tasks[task_id]
    if task["status"] != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="Task not completed"
        )
        
    if not task["result_path"] or not os.path.exists(task["result_path"]):
        raise HTTPException(
            status_code=404,
            detail="Result file not found"
        )
        
    return FileResponse(
        task["result_path"],
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(task["result_path"])
    )

@app.get("/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    } 