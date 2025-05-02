# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import warnings

from typing_extensions import Self

from . import model


class Action(model.ModelEntity):
    def __init__(self, entity_id, model, history_index=-1, connected=True):
        super().__init__(entity_id, model, history_index, connected)
        self.results = {}
        self._status = self.data["status"]

    @property
    def status(self):
        # FullStatus doesn't contain actions or their results
        # However. there's a Delta that updates these objects
        # And these objects are exposed via e.g. Unit.run_action(), common in integration tests
        warnings.warn("FIXME gotta work on Actions", stacklevel=2)
        return self._status

    async def fetch_output(self) -> None:
        completed_action = await self.model._get_completed_action(self.id)
        self.results = completed_action.output or {}
        self._status = completed_action.status

    async def wait(self) -> Self:
        if not self.results:
            await self.fetch_output()
        return self
