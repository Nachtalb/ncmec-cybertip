"""Presence-flag empty XML elements (e.g. ``<sextortion/>``).

Several schema elements carry meaning purely by their presence: an empty
``<sextortion/>`` tag means "yes, sextortion". This module exposes :data:`Flag`,
an ``Annotated`` type that lets callers work with plain ``bool`` values while the
model serialises them as a present-or-absent empty element.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator, PlainSerializer
from pydantic_xml import BaseXmlModel


class _Empty(BaseXmlModel):
    """An element that carries meaning by its presence alone."""


def _to_empty(value: Any) -> _Empty | None:
    """Coerce a ``bool``/``None``/``_Empty`` input into ``_Empty | None``."""
    if value is True:
        return _Empty()
    if value is False or value is None:
        return None
    if isinstance(value, _Empty):
        return value
    msg = f"flag value must be bool, None, or _Empty, got {type(value).__name__}"
    raise TypeError(msg)


def _from_empty(value: _Empty | None) -> bool:
    """Render the stored value back to a plain ``bool`` for ``model_dump``."""
    return value is not None


Flag = Annotated[
    _Empty | None,
    BeforeValidator(_to_empty),
    PlainSerializer(_from_empty, return_type=bool, when_used="json"),
]
"""A presence flag: ``True`` emits an empty element, ``False``/``None`` omits it."""
