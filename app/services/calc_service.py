from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
import ast
import operator as op

from app.models.calculation import Calculation
from app.services.calculator import calculate

# Allowed operators for expression evaluation
_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def _safe_eval(expr: str) -> float:
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return _ALLOWED_OPS[type(node.op)](
                _eval(node.left), _eval(node.right)
            )
        elif isinstance(node, ast.UnaryOp):
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        else:
            raise ValueError("Invalid expression")

    tree = ast.parse(expr, mode="eval")
    return float(_eval(tree.body))


def create_calculation(
    db: Session,
    user_id: int,
    op: str | None = None,
    a: float | None = None,
    b: float | None = None,
    expression: str | None = None,
) -> Calculation:

    if expression:
        result = _safe_eval(expression)
        calc = Calculation(
            user_id=user_id,
            expression=expression,
            result=result,
        )
    else:
        result = calculate(op, a, b)
        calc = Calculation(
            user_id=user_id,
            op=op.lower().strip(),
            a=a,
            b=b,
            result=result,
        )

    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


def list_calculations(db: Session, user_id: int, limit: int = 20):
    return list(
        db.execute(
            select(Calculation)
            .where(Calculation.user_id == user_id)
            .order_by(desc(Calculation.created_at))
            .limit(limit)
        ).scalars().all()
    )


def get_stats(db: Session, user_id: int) -> dict:
    total = db.execute(
        select(func.count(Calculation.id)).where(Calculation.user_id == user_id)
    ).scalar_one()

    avg = db.execute(
        select(func.avg(Calculation.result)).where(Calculation.user_id == user_id)
    ).scalar_one()

    last_op = db.execute(
        select(Calculation.op)
        .where(Calculation.user_id == user_id)
        .order_by(desc(Calculation.created_at))
        .limit(1)
    ).scalar_one_or_none()

    return {
        "total_calculations": int(total or 0),
        "average_result": float(avg or 0.0),
        "last_operation": last_op,
    }


def get_all_calculations(db: Session, user_id: int):
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == user_id)
        .order_by(Calculation.id.desc())
        .all()
    )
