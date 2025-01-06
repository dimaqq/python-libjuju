# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

from typing import Protocol

from juju.client._definitions import (
    ApplicationGetResults,
    ApplicationInfoResults,
    Entity,
    FullStatus,
)


class ApplicationFacadeProtocol(Protocol):
    async def Get(self, application=None, branch=None) -> ApplicationGetResults: ...  # noqa: N802

    # jRRC Params={"entities":[{"tag": "yada-yada"}]}
    # codegen unpacks top-level keys into keyword arguments
    async def ApplicationsInfo(  # noqa: N802
        self, entities: list[Entity]
    ) -> ApplicationInfoResults: ...

    # ...


class CharmsFacadeProtocol(Protocol): ...


class ClientFacadeProtocol(Protocol):
    async def FullStatus(self, include_storage=None, patterns=None) -> FullStatus: ...  # noqa: N802
