# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
"""Tentative interface to individual watchers post-all-watcher."""

from __future__ import annotations

# Tentative endpoint to track Action progress and completion
"""
Action: 7
.WatchActionsProgress()
in: Entities
.entities[0]: Entity
.entities[0].tag: str
out: StringsWatchResults
.results[0]: StringsWatchResult
.results[0].changes[0]: str      # <-- what's in this array of strings, only action log?
.results[0].error: Error         # <-- is that a hard error or a failed action?
.results[0].error.code: str      # <-- how do we know when it's over?
.results[0].error.info["abc"]: dict[Any, Any]
.results[0].error.message: str
.results[0].watcher-id: str
"""

# A single .run() can be broadcast across units
# Thus, we get one or a bunch of Action entity ids
# Actions.Action(...ids) or Actions.ListOperations(...) can be used to query actions
# the result includes the .completed flag
