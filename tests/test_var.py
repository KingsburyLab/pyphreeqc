from pytest import approx
from pyphreeqc.interface import Var
from pyphreeqc._bindings import PY_VRESULT


def test_var_new():
    var = Var()
    assert var.value is None


def test_var_int():
    var = Var(42)
    assert var.value == 42


def test_var_float():
    var = Var(3.1415926)
    assert var.value == approx(3.1415926)


def test_var_str():
    var = Var("Hello World")
    assert var.value == "Hello World"


def test_var_error():
    var = Var(PY_VRESULT.VR_OUTOFMEMORY)
    assert var.value == PY_VRESULT.VR_OUTOFMEMORY


def test_var_empty():
    var = Var(None)
    assert var.value is None


def test_var_modify():
    var = Var("Hello World")
    var.value = 42
    assert var.value == 42