import math
import ast
import operator as op


ALLOWED_OPS = {"add", "sub", "mul", "div", "mod", "pow"}


def calculate(op_name: str, a: float, b: float) -> float:
    op_name = op_name.lower().strip()
    if op_name not in ALLOWED_OPS:
        raise ValueError(f"Unsupported operation: {op_name}")

    if op_name == "add":
        return a + b
    if op_name == "sub":
        return a - b
    if op_name == "mul":
        return a * b
    if op_name == "div":
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b
    if op_name == "mod":
        if b == 0:
            raise ZeroDivisionError("Modulus by zero")
        return a % b
    if op_name == "pow":
        if abs(a) > 1e6 or abs(b) > 1e3:
            raise ValueError("Inputs too large for pow")
        return float(math.pow(a, b))

    raise ValueError("Invalid operation")


# Multi-level expression

_ALLOWED_AST_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}

_ALLOWED_AST_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}


def evaluate_expression(expression: str) -> float:
    """
    Safely evaluate expressions like:
      (5 + 3) * 2
      10 / (2 + 3)
      2^3 + 4   (we treat ^ as power)
    Allowed: numbers, + - * / % ** parentheses, unary +/-
    """
    if expression is None:
        raise ValueError("Expression is required")

    expr = expression.strip()
    if not expr:
        raise ValueError("Expression is required")

    # Support caret power used in many calculators
    expr = expr.replace("^", "**")

    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid expression syntax")

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.Expression):
            return _eval(n.body)

        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)

        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_AST_UNARYOPS:
            return float(_ALLOWED_AST_UNARYOPS[type(n.op)](_eval(n.operand)))

        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_AST_BINOPS:
            left = _eval(n.left)
            right = _eval(n.right)

            if isinstance(n.op, (ast.Div, ast.Mod)) and right == 0:
                raise ZeroDivisionError("Division by zero")

            # small guardrails for huge exponent
            if isinstance(n.op, ast.Pow) and (abs(left) > 1e6 or abs(right) > 1e3):
                raise ValueError("Inputs too large for exponentiation")

            return float(_ALLOWED_AST_BINOPS[type(n.op)](left, right))

        raise ValueError("Unsupported expression content")

    return float(_eval(node))
