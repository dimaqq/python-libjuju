# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
# FIXME temp only, don't merge this file
from __future__ import annotations

import asyncio
import logging
import os
import pprint

from juju.model import Model

MODEL = os.environ.get("MODEL", "testm")


async def main() -> None:
    m = Model()
    await m.connect(model_name=MODEL)
    # from juju.client._client import CharmsFacade
    # f = CharmsFacade.from_connection(m.connection())
    # rv = await f.CharmInfo("local:noble/fake-ingress-0")
    # print(rv)
    # print()

    # FIXME a little later
    # app = ApplicationFacade.from_connection(m.connection())
    # rv = await app.UnitsInfo()
    # print(rv)

    # rv = await f.ApplicationsInfo(entities=[{"tag": "application-database"}])
    # print(rv)
    # print()

    for app_name, app in m.applications.items():
        pprint.pprint(app.model.state.state["application"][app_name][-1])

        # Deprecated:
        # owner_tag.......... {app.owner_tag!r}
        # min_units.......... {app.min_units!r}
        print(f"""{app_name}:
        name............... {app.name!r}
        charm_name......... {app.charm_name!r}
        exposed............ {app.exposed!r}
        charm_url.......... {app.charm_url!r}
        life............... {app.life!r}
        constraints["arch"] {app.constraints["arch"]!r}
        subordinate........ {app.subordinate!r}
        status............. {app.status!r}
        workload_version... {app.workload_version!r}
        """)
        for u in app.units:
            print(f"{u.name}: {u.agent_status!r} {u.workload_status!r}")

    # __import__("pdb").set_trace()
    await m.wait_for_idle(idle_period=1)

    await m.disconnect()


class SymbolFormatter(logging.Formatter):
    levels = {
        "DEBUG": "🐛",
        "INFO": "ℹ️",  # noqa: RUF001
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }
    threads: dict[str | None, str] = {
        "MainThread": "🧵",
        "Kubernetes": "☸️",
        "AsyncRunner": "🏃",
        "Thread-1": "1️⃣",
        "Thread-2": "2️⃣",
    }

    def format(self, record) -> str:
        level = self.levels.get(record.levelname, "#")
        thread = self.threads.get(record.threadName, record.threadName)
        task = getattr(record, "taskName", "~")
        message = record.getMessage()
        return f"{level} {thread} {task} {message}"


async def wrapped_main():
    await asyncio.create_task(main(), name="Main")


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG" if os.environ.get("DEBUG") else "INFO")
    logging.root.handlers[0].setFormatter(SymbolFormatter())
    asyncio.run(wrapped_main())
