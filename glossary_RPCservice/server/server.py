from concurrent import futures
import subprocess
import sys
from typing import Optional
from pathlib import Path

import grpc
from sqlalchemy.orm import Session

# Ensure project root is on sys.path for absolute imports like `app.*`
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import SessionLocal, engine
from app import models

import glossary_pb2 as pb
import glossary_pb2_grpc as rpc


def try_run_migrations() -> None:
    """Attempt to run Alembic migrations; fall back to create_all if Alembic is unavailable."""
    try:
        # Try running alembic upgrade head (assumes alembic.ini present in project root)
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    except Exception:
        # Fallback: ensure tables exist
        models.Base.metadata.create_all(bind=engine)


class GlossaryService(rpc.GlossaryServiceServicer):
    def _to_msg(self, term: models.Term) -> pb.Term:
        return pb.Term(keyword=term.keyword, description=term.description)

    def ListTerms(self, request: pb.ListTermsRequest, context: grpc.ServicerContext) -> pb.ListTermsResponse:
        with SessionLocal() as db:  # type: Session
            items = db.query(models.Term).all()
            return pb.ListTermsResponse(items=[self._to_msg(t) for t in items])

    def GetTerm(self, request: pb.GetTermRequest, context: grpc.ServicerContext) -> pb.GetTermResponse:
        with SessionLocal() as db:
            term: Optional[models.Term] = db.query(models.Term).filter_by(keyword=request.keyword).first()
            if term is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Term not found")
            return pb.GetTermResponse(item=self._to_msg(term))

    def CreateTerm(self, request: pb.CreateTermRequest, context: grpc.ServicerContext) -> pb.CreateTermResponse:
        with SessionLocal() as db:
            existing = db.query(models.Term).filter_by(keyword=request.item.keyword).first()
            if existing is not None:
                context.abort(grpc.StatusCode.ALREADY_EXISTS, "Keyword already exists")
            term = models.Term(keyword=request.item.keyword, description=request.item.description)
            db.add(term)
            db.commit()
            db.refresh(term)
            return pb.CreateTermResponse(item=self._to_msg(term))

    def UpdateTerm(self, request: pb.UpdateTermRequest, context: grpc.ServicerContext) -> pb.UpdateTermResponse:
        with SessionLocal() as db:
            term: Optional[models.Term] = db.query(models.Term).filter_by(keyword=request.item.keyword).first()
            if term is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Term not found")
            term.description = request.item.description
            db.commit()
            db.refresh(term)
            return pb.UpdateTermResponse(item=self._to_msg(term))

    def DeleteTerm(self, request: pb.DeleteTermRequest, context: grpc.ServicerContext) -> pb.DeleteTermResponse:
        with SessionLocal() as db:
            term: Optional[models.Term] = db.query(models.Term).filter_by(keyword=request.keyword).first()
            if term is None:
                context.abort(grpc.StatusCode.NOT_FOUND, "Term not found")
            db.delete(term)
            db.commit()
            return pb.DeleteTermResponse(ok=True)


def serve() -> None:
    try_run_migrations()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_GlossaryServiceServicer_to_server(GlossaryService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()


