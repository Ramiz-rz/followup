import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.document_parser import parse_document, DocumentParseError
from app.services.pipeline import run_analysis
from app.services.persist import persist_analysis

router = APIRouter(prefix="/api", tags=["analyze"])

DEMO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "sample_data",
    "demo_conversation.txt",
)


def _run_and_build_project(db: Session, text: str, project_name: str, source_name: str) -> models.Project:
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Add some conversation text first.")

    try:
        pipeline_result = run_analysis(text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project = models.Project(
        name=project_name.strip() if project_name and project_name.strip() else "Untitled analysis",
        summary=pipeline_result.result.summary,
        source_text=text,
        source_name=source_name,
        analysis_mode=pipeline_result.mode,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    persist_analysis(db, project, pipeline_result.result, source_name)

    return project, pipeline_result.mode, pipeline_result.note


@router.post("/analyze", response_model=schemas.ProjectOut)
async def analyze(
    text: str = Form(None),
    project_name: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    if file is not None and file.filename:
        raw_bytes = await file.read()
        try:
            parsed_text = parse_document(file.filename, raw_bytes)
        except DocumentParseError as e:
            raise HTTPException(status_code=400, detail=str(e))
        source_name = file.filename
    elif text:
        parsed_text = text
        source_name = "pasted conversation"
    else:
        raise HTTPException(status_code=400, detail="Add some conversation text first.")

    project, mode, note = _run_and_build_project(db, parsed_text, project_name or "", source_name)
    response = schemas.ProjectOut.model_validate(project)
    return response


@router.post("/projects/{project_id}/analyze", response_model=schemas.ProjectOut)
async def analyze_into_project(
    project_id: str,
    text: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if file is not None and file.filename:
        raw_bytes = await file.read()
        try:
            parsed_text = parse_document(file.filename, raw_bytes)
        except DocumentParseError as e:
            raise HTTPException(status_code=400, detail=str(e))
        source_name = file.filename
    elif text:
        parsed_text = text
        source_name = "pasted conversation"
    else:
        raise HTTPException(status_code=400, detail="Add some conversation text first.")

    try:
        pipeline_result = run_analysis(parsed_text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    project.summary = pipeline_result.result.summary
    project.source_text = (project.source_text or "") + "\n\n" + parsed_text
    project.analysis_mode = pipeline_result.mode
    db.commit()

    persist_analysis(db, project, pipeline_result.result, source_name)
    db.refresh(project)
    return project


@router.post("/demo", response_model=schemas.ProjectOut)
def run_demo(db: Session = Depends(get_db)):
    try:
        with open(DEMO_PATH, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Demo conversation file is missing.")

    project, mode, note = _run_and_build_project(db, text, "Atlas Client Portal (Demo)", "demo_conversation.txt")
    return project
