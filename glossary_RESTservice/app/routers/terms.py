from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Term
from ..schemas import TermCreate, TermUpdate, TermOut


router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("", response_model=list[TermOut], summary="List all terms")
def list_terms(db: Session = Depends(get_db)):
    try:
        terms = db.execute(select(Term)).scalars().all()
        return terms
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


@router.get("/{keyword}", response_model=TermOut, summary="Get term by keyword")
def get_term(keyword: str, db: Session = Depends(get_db)):
    try:
        term = db.execute(select(Term).where(Term.keyword == keyword)).scalar_one_or_none()
        if term is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
        return term
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


@router.post("", response_model=TermOut, status_code=status.HTTP_201_CREATED, summary="Create term")
def create_term(payload: TermCreate, db: Session = Depends(get_db)):
    try:
        existing = db.execute(select(Term).where(Term.keyword == payload.keyword)).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Term with this keyword already exists")
        term = Term(keyword=payload.keyword, description=payload.description)
        db.add(term)
        db.commit()
        db.refresh(term)
        return term
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


@router.put("/{keyword}", response_model=TermOut, summary="Update term by keyword")
def update_term(keyword: str, payload: TermUpdate, db: Session = Depends(get_db)):
    try:
        term = db.execute(select(Term).where(Term.keyword == keyword)).scalar_one_or_none()
        if term is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")

        if payload.keyword is not None and payload.keyword != term.keyword:
            conflict = db.execute(select(Term).where(Term.keyword == payload.keyword)).scalar_one_or_none()
            if conflict is not None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another term with this keyword exists")
            term.keyword = payload.keyword

        if payload.description is not None:
            term.description = payload.description

        db.commit()
        db.refresh(term)
        return term
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


@router.delete("/{keyword}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete term by keyword")
def delete_term(keyword: str, db: Session = Depends(get_db)):
    try:
        term = db.execute(select(Term).where(Term.keyword == keyword)).scalar_one_or_none()
        if term is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
        db.delete(term)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")


