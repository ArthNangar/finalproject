from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from app.db.session import get_db
from app.routes.deps import get_current_user
from app.schemas.calculation import CalcIn, CalcOut, StatsOut, ExpressionIn
from app.services.calc_service import (
    create_calculation,
    list_calculations,
    get_stats,
    get_all_calculations,
)
from app.services.calculator import evaluate_expression

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/calculate", response_model=CalcOut)
def api_calculate(
    payload: CalcIn,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_calculation(
            db=db,
            user_id=user.id,
            op=payload.op,
            a=payload.a,
            b=payload.b,
        )
    except ZeroDivisionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate/expression")
def api_calculate_expression(
    payload: ExpressionIn,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns: { "result": <number> }
    (Optional) You can also store it in DB if your model supports `expression`.
    """
    try:
        result = evaluate_expression(payload.expression)
        return {"result": result}
    except ZeroDivisionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/history", response_model=list[CalcOut])
def api_history(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
):
    return list_calculations(db, user_id=user.id, limit=limit)


@router.get("/stats", response_model=StatsOut)
def api_stats(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_stats(db, user_id=user.id)


@router.get("/export/history")
def export_history_csv(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    calculations = get_all_calculations(db, user_id=user.id)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["operation", "a", "b", "expression", "result"])

    for c in calculations:
        writer.writerow([
            getattr(c, "op", None),
            getattr(c, "a", None),
            getattr(c, "b", None),
            getattr(c, "expression", None),
            getattr(c, "result", None),
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=calculation_history.csv"},
    )


@router.post("/undo/push")
def push_undo(request: Request, payload: dict):
    session = request.session
    undo_stack = session.get("undo_stack", [])
    undo_stack.append(payload)
    session["undo_stack"] = undo_stack
    session["redo_stack"] = []
    return {"status": "ok"}


@router.post("/undo/pop")
def undo_calculation(request: Request):
    session = request.session
    undo_stack = session.get("undo_stack", [])
    redo_stack = session.get("redo_stack", [])

    if not undo_stack:
        return {"status": "empty"}

    last = undo_stack.pop()
    redo_stack.append(last)

    session["undo_stack"] = undo_stack
    session["redo_stack"] = redo_stack

    return {"status": "ok", "calculation": last}


@router.post("/redo")
def redo_calculation(request: Request):
    session = request.session
    undo_stack = session.get("undo_stack", [])
    redo_stack = session.get("redo_stack", [])

    if not redo_stack:
        return {"status": "empty"}

    calc = redo_stack.pop()
    undo_stack.append(calc)

    session["undo_stack"] = undo_stack
    session["redo_stack"] = redo_stack

    return {"status": "ok", "calculation": calc}
