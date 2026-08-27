"""Evaluate the bare arithmetic students occasionally send.

"2+2?" was answered with the generic off-topic deflection (A5). Refusing to add
two numbers reads as broken to a student at a tuition centre, and there is no
reason to send it round the LLM: a bounded expression evaluator answers it
exactly, instantly, and without a model call.

Only literal arithmetic is accepted — no names, no calls, no attribute access —
so this cannot become an execution path for user input.
"""

from __future__ import annotations

import ast
import operator
import re

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

#: A message that is nothing but an arithmetic expression, optionally ending in
#: "=" or "?". Anything with a word in it is a sentence, not a sum.
_BARE_EXPRESSION_RE = re.compile(r"^[\d\s()+\-*/%.^]+[=?]*$")

#: Guards against expressions that are cheap to type and expensive to evaluate.
_MAX_LENGTH = 60
_MAX_ABS_EXPONENT = 64


def looks_like_arithmetic(message: str) -> bool:
    text = (message or "").strip()
    if not text or len(text) > _MAX_LENGTH:
        return False
    if not any(op in text for op in "+-*/%^"):
        return False
    return bool(_BARE_EXPRESSION_RE.match(text))


def evaluate_arithmetic(message: str) -> str | None:
    """Return the formatted result, or ``None`` if this isn't plain arithmetic."""
    if not looks_like_arithmetic(message):
        return None

    expression = (message or "").strip().rstrip("?=").strip().replace("^", "**")
    if not expression:
        return None

    try:
        tree = ast.parse(expression, mode="eval")
        value = _evaluate(tree.body)
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
        return None

    return _format(value)


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("only numbers are allowed")
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BINARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError("unsupported operator")
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_ABS_EXPONENT:
            raise ValueError("exponent too large")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError("unsupported unary operator")
        return op(_evaluate(node.operand))
    raise ValueError("unsupported expression")


def _format(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{round(value, 6):g}"
    return str(value)


__all__ = ["evaluate_arithmetic", "looks_like_arithmetic"]
