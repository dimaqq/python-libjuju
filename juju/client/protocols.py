# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

from typing import Protocol

from juju.client._definitions import (
    ApplicationGetResults,
    ApplicationInfoResults,
    Entity,
)


class ApplicationFacadeProtocol(Protocol):
    async def Get(self, application=None, branch=None) -> ApplicationGetResults: ...  # noqa: N802

    # jRRC Params={"entities":[{"tag": "yada-yada"}]}
    # codegen unpacks top-level keys into keyword arguments
    async def ApplicationsInfo(  # noqa: N802
        self, entities: list[Entity]
    ) -> ApplicationInfoResults: ...

    # etc...
    # etc...
    # etc...
    # etc...
    # etc...
    # etc...


class CharmsFacadeProtocol(Protocol): ...


class UniterFacadeProtocol(Protocol): ...
