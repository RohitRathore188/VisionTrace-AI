"""
Case Management API Endpoints (v1)
FastAPI router for security incident cases, investigations, and case files
"""

import uuid
from datetime import datetime
from typing import Annotated, List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.case import Case, CaseStatus, CasePriority

router = APIRouter(prefix="/cases", tags=["Case Management"])


class CaseResponse(BaseModel):
    id: uuid.UUID
    case_number: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assigned_investigator_id: Optional[uuid.UUID] = None
    created_by_id: uuid.UUID
    notes_json: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    priority: CasePriority = Field(default=CasePriority.MEDIUM)
    assigned_investigator_id: Optional[uuid.UUID] = None


class CaseNoteRequest(BaseModel):
    note: str = Field(..., min_length=1)


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all security incident cases"""
    stmt = select(Case).where(Case.is_deleted == False).order_by(desc(Case.created_at))
    res = await db.execute(stmt)
    cases = list(res.scalars().all())

    # Seed initial cases if empty
    if not cases:
        try:
            # Check if user exists in DB
            user_stmt = select(User).where(User.id == current_user.id)
            user_res = await db.execute(user_stmt)
            valid_user_id = current_user.id if user_res.scalar_one_or_none() else None

            c1 = Case(
                id=uuid.uuid4(),
                case_number="INV-2026-00101",
                title="Unauthorized Perimeter Intrusion at Gate 3",
                description="Person observed attempting unauthorized access near North Fence line at 22:15 hrs.",
                status=CaseStatus.INVESTIGATING,
                priority=CasePriority.HIGH,
                created_by_id=valid_user_id,
                notes_json=[{
                    "timestamp": datetime.utcnow().isoformat(),
                    "author": current_user.email,
                    "text": "Initial case opened. Keyframe evidence associated."
                }]
            )
            c2 = Case(
                id=uuid.uuid4(),
                case_number="INV-2026-00102",
                title="Vehicle Overstay Investigation — Parking Bay 4",
                description="Black SUV parked in restricted loading zone exceeding 2-hour policy window.",
                status=CaseStatus.OPEN,
                priority=CasePriority.MEDIUM,
                created_by_id=valid_user_id,
                notes_json=[{
                    "timestamp": datetime.utcnow().isoformat(),
                    "author": current_user.email,
                    "text": "Vehicle visual search executed across CAM-01 and CAM-02."
                }]
            )
            db.add_all([c1, c2])
            await db.commit()
            res = await db.execute(stmt)
            cases = list(res.scalars().all())
        except Exception as e:
            await db.rollback()
            cases = []

    return cases


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new incident case file"""
    case_num = f"INV-2026-{uuid.uuid4().hex[:6].upper()}"
    try:
        user_stmt = select(User).where(User.id == current_user.id)
        user_res = await db.execute(user_stmt)
        valid_user_id = current_user.id if user_res.scalar_one_or_none() else None

        priority_val = payload.priority
        new_case = Case(
            id=uuid.uuid4(),
            case_number=case_num,
            title=payload.title,
            description=payload.description,
            status=CaseStatus.OPEN,
            priority=priority_val,
            assigned_investigator_id=valid_user_id,
            created_by_id=valid_user_id,
            notes_json=[{
                "timestamp": datetime.utcnow().isoformat(),
                "author": current_user.email,
                "text": f"Case file {case_num} created."
            }]
        )
        db.add(new_case)

        from app.models.audit import AuditLog
        audit = AuditLog(
            user_id=valid_user_id,
            user_email=current_user.email,
            action="CASE_CREATE",
            resource_type="case",
            resource_id=case_num,
            result_status="SUCCESS",
            details_json={"title": payload.title, "priority": priority_val.value}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(new_case)
        return new_case
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create case: {str(e)}")


@router.post("/{case_id}/notes", response_model=CaseResponse)
async def add_case_note(
    case_id: uuid.UUID,
    payload: CaseNoteRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Append investigator note to case record"""
    stmt = select(Case).where(Case.id == case_id, Case.is_deleted == False)
    res = await db.execute(stmt)
    case_obj = res.scalar_one_or_none()
    if not case_obj:
        raise HTTPException(status_code=404, detail="Case file not found")

    new_notes = list(case_obj.notes_json or [])
    new_notes.append({
        "timestamp": datetime.utcnow().isoformat(),
        "author": current_user.email,
        "text": payload.note
    })
    case_obj.notes_json = new_notes
    await db.commit()
    await db.refresh(case_obj)
    return case_obj
