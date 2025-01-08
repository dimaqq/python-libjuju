# Copyright 2025 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
# FIXME temp only, don't merge this file
import logging
import pprint

from juju import jasyncio
from juju.model import Model


async def main() -> None:
    m = Model()
    await m.connect(model_name="testm")
    # from juju.client._client import CharmsFacade
    # f = CharmsFacade.from_connection(m.connection())
    # rv = await f.CharmInfo("local:noble/fake-ingress-0")
    # print(rv)
    # print()
    from juju.client._client import ApplicationFacade

    app = ApplicationFacade.from_connection(m.connection())
    rv = await app.UnitsInfo()
    print(rv)

    # rv = await f.ApplicationsInfo(entities=[{"tag": "application-database"}])
    # print(rv)
    # print()

    for app_name, app in m.applications.items():
        pprint.pprint(app.model.state.state["application"][app_name][-1])
        print(f"""{app_name}:
        name............... {app.name!r}
        charm_name......... {app.charm_name!r}
        exposed............ {app.exposed!r}
        charm_url.......... {app.charm_url!r}
        owner_tag.......... {app.owner_tag!r}
        life............... {app.life!r}
        min_units.......... {app.min_units!r}
        constraints["arch"] {app.constraints["arch"]!r}
        subordinate........ {app.subordinate!r}
        status............. {app.status!r}
        workload_version... {app.workload_version!r}
        """)
        for u in app.units:
            print(f"{u.name}: {u.agent_status!r} {u.workload_status!r}")

    await m.wait_for_idle()

    await m.disconnect()


class SymbolFilter(logging.Filter):
    DEBUG = "🐛"
    INFO = "ℹ️"  # noqa: RUF001
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "🔥"

    def filter(self, record):
        record.symbol = getattr(self, record.levelname, "#")
        # FIXME can control log record origin here if needed
        return True


if __name__ == "__main__":
    # FIXME why is level=DEBUG broken?
    # logging.basicConfig(level="INFO", format="%(symbol)s %(message)s")
    # logging.root.addFilter(SymbolFilter())
    jasyncio.run(main())
