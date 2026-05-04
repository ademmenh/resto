from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

UnitValue = Literal["kg", "l", "m3", "g"]

_KNOWN: frozenset[str] = frozenset({"kg", "l", "m3", "g"})


@dataclass(frozen=True)
class Unit:
    """
    Value object for inventory measurement units.
    Allowed values: kg, l, m3, g.
    """

    value: UnitValue

    @classmethod
    def create(cls, raw: str) -> Unit:
        if raw not in _KNOWN:
            allowed = ", ".join(sorted(_KNOWN))
            raise ValueError(f"Unknown unit {raw!r}. Allowed values: {allowed}")
        return cls(value=raw)  # type: ignore[arg-type]

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Unit({self.value!r})"
