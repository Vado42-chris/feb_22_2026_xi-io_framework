"""Terminal progress helpers with no external deps."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def with_spinner(message: str) -> Iterator[None]:
    print(message)
    yield


@contextmanager
def with_progress(total: int, desc: str, unit: str = "items") -> Iterator[None]:
    print(f"{desc} (total={total} {unit})")
    yield
