from typing import Any
from pyphreeqc._bindings import PyVar, PY_VAR_TYPE, PY_VRESULT, PyIPhreeqc

IPhreeqc = PyIPhreeqc


class Var:
    def __init__(self, value: Any | None = None):
        self._var = PyVar()
        self._var.var.type = PY_VAR_TYPE.TT_EMPTY
        self.value = value

    @property
    def value(self) -> Any:
        match self._var.var.type:
            case PY_VAR_TYPE.TT_EMPTY:
                return None
            case PY_VAR_TYPE.TT_ERROR:
                return self._var.var.vresult
            case PY_VAR_TYPE.TT_LONG:
                return self._var.var.lVal
            case PY_VAR_TYPE.TT_DOUBLE:
                return self._var.var.dVal
            case PY_VAR_TYPE.TT_STRING:
                return self._var.var.sVal
            case _:
                raise RuntimeError("Unknown type")

    @value.setter
    def value(self, value) -> None:
        if isinstance(value, PY_VRESULT):
            self._var.var.type = PY_VAR_TYPE.TT_ERROR
            self._var.var.vresult = value
        elif isinstance(value, int):
            self._var.var.type = PY_VAR_TYPE.TT_LONG
            self._var.var.lVal = value
        elif isinstance(value, float):
            self._var.var.type = PY_VAR_TYPE.TT_DOUBLE
            self._var.var.dVal = value
        elif isinstance(value, str):
            self._var.var.type = PY_VAR_TYPE.TT_STRING
            self._var.var.sVal = value
        elif value is None:
            self._var.var.type = PY_VAR_TYPE.TT_EMPTY
        else:
            raise RuntimeError("Unknown type")


class Phreeqc:
    def __init__(self):
        self._ext = PyIPhreeqc()
        # TODO: Is VAR the common denominator for most operations?
        # Here we create one and modify it in operations instead of having
        # the caller create new VARs per operation.
        self._var = Var()

    def __getattr__(self, item) -> None:
        """Delegate attribute access to the underlying PyIPhreeqc instance."""
        if hasattr(self._ext, item):
            return getattr(self._ext, item)
        raise AttributeError(f"{type(self).__name__} has no attribute '{item}'")

    def __getitem__(self, item) -> Any:
        if not isinstance(item, tuple):
            item = (item,)
        while len(item) < 2:
            item += (slice(None),)

        row_idx, col_idx = item

        if isinstance(row_idx, slice):
            row_indices = range(*row_idx.indices(self.shape[0]))
        elif isinstance(row_idx, int):
            row_indices = [row_idx]
        else:
            raise TypeError("Row index must be int or slice")

        if isinstance(col_idx, slice):
            col_indices = range(*col_idx.indices(self.shape[1]))
        elif isinstance(col_idx, int):
            col_indices = [col_idx]
        else:
            raise TypeError("Column index must be int or slice")

        result = []
        for row in row_indices:
            row_values = []
            for col in col_indices:
                self._ext.get_value(row, col, self._var._var.var)
                row_values.append(self._var.value)
            result.append(
                row_values if len(col_indices) > 1 else row_values[0])

        if len(row_indices) == 1:
            return result[0]
        return result

    @property
    def shape(self) -> tuple[int, int]:
        return self.get_selected_output_row_count(), self.get_selected_output_column_count()