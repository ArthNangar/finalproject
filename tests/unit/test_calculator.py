import pytest
from app.services.calculator import calculate

def test_add():
    assert calculate("add", 2, 3) == 5

def test_mod():
    assert calculate("mod", 10, 3) == 1

def test_pow():
    assert calculate("pow", 2, 3) == 8.0

def test_div_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("div", 1, 0)

def test_invalid_op():
    with pytest.raises(ValueError):
        calculate("sqrt", 9, 0)

def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("div", 10, 0)

def test_mod_by_zero():
    with pytest.raises(ZeroDivisionError):
        calculate("mod", 10, 0)

def test_invalid_operation():
    with pytest.raises(ValueError):
        calculate("bad", 1, 2)

def test_pow_limits():
    with pytest.raises(ValueError):
        calculate("pow", 1e9, 2)