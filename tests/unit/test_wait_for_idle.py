# Copyright 2024 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

import copy
import json
import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import reveal_type as reveal_type
from unittest.mock import Mock

from juju.application import Application
from juju.client.facade import _convert_response
from juju.client._definitions import FullStatus
from juju.errors import JujuAgentError, JujuAppError, JujuMachineError, JujuUnitError
from juju.machine import Machine
from juju.model import Model
from juju.unit import Unit


async def test_no_apps(full_status_response: dict, kwargs: dict):
    kwargs["apps"] = []
    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_missing_app(full_status_response: dict, kwargs: dict):
    kwargs["apps"] = ["missing"]
    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert not idle and not legacy


async def test_no_units(full_status_response: dict, kwargs: dict):
    full_status_response["response"]["applications"]["hexanator"]["units"].clear()
    kwargs["apps"] = ["hexanator"]
    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle == legacy
    assert not idle and not legacy


async def test_naive(full_status_response: dict, kwargs: dict):
    kwargs["apps"] = ["hexanator"]
    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_app_error(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["status"]["status"] = "error"
    app["status"]["info"] = "big problem"

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_error"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuAppError)
    assert isinstance(legacy, JujuAppError)
    assert "big problem" in str(idle) and "in error" in str(legacy)


async def test_exact_count(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_exact_units"] = 2

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


@pytest.mark.parametrize("wrong_count", [1, 3])
async def test_wrong_exact_count(full_status_response: dict, kwargs: dict, wrong_count: int):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_exact_units"] = wrong_count

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert not idle and not legacy


async def test_exact_count_precedence(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_exact_units"] = 2
    kwargs["wait_for_at_least_units"] = 9
    kwargs["_wait_for_units"] = 9

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_ready_unit_count(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_at_least_units"] = 2
    kwargs["_wait_for_units"] = 2
    kwargs["status"] = "active"

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_ready_unit_requires_idle_agent(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])
    app["units"]["hexanator/1"]["agent-status"]["status"] = "some-other"

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_at_least_units"] = 2
    kwargs["_wait_for_units"] = 2
    kwargs["status"] = "active"

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert not idle and not legacy


async def test_ready_unit_requires_workload_status(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/1"] = copy.deepcopy(app["units"]["hexanator/0"])
    app["units"]["hexanator/1"]["workload-status"]["status"] = "some-other"

    kwargs["apps"] = ["hexanator"]
    kwargs["wait_for_at_least_units"] = 2
    kwargs["_wait_for_units"] = 2
    kwargs["status"] = "active"

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert not idle and not legacy

# FIXME eventual timeout

async def test_agent_error(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/0"]["agent-status"]["status"] = "error"
    app["units"]["hexanator/0"]["agent-status"]["info"] = "agent problem"

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_error"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuAgentError)
    assert isinstance(legacy, JujuAgentError)
    assert "hexanator/0" in str(idle) and "hexanator/0" in str(legacy)
    assert "agent problem" in str(idle) and "in error" in str(legacy)


async def test_workload_error(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/0"]["workload-status"]["status"] = "error"
    app["units"]["hexanator/0"]["workload-status"]["info"] = "workload problem"

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_error"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuUnitError)
    assert isinstance(legacy, JujuUnitError)
    assert "hexanator/0" in str(idle) and "hexanator/0" in str(legacy)
    assert "workload problem" in str(idle) and "in error" in str(legacy)


async def test_machine_ok(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/0"]["machine"] = "42"
    # https://github.com/dimaqq/juju-schema-analysis/blob/main/schemas-juju-3.5.4.txt#L3611-L3674
    full_status_response["response"]["machines"] = {
        "42": {
            "instance-status": {
                "status": "running",
                "info": "RUNNING",
            },
        },
    }

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_error"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_machine_error(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/0"]["machine"] = "42"
    full_status_response["response"]["machines"] = {
        "42": {
            "instance-status": {
                "status": "error",
                "info": "Battery low. Try a potato?",
            },
        },
    }

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_error"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuMachineError)
    assert isinstance(legacy, JujuMachineError)
    assert "potato" in str(idle) and "error" in str(legacy)


async def test_app_blocked(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["status"]["status"] = "blocked"
    app["status"]["info"] = "big problem"

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_blocked"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuAppError)
    assert isinstance(legacy, JujuAppError)
    assert "big problem" in str(idle) and "blocked" in str(legacy)


async def test_unit_blocked(full_status_response: dict, kwargs: dict):
    app = full_status_response["response"]["applications"]["hexanator"]
    app["units"]["hexanator/0"]["workload-status"]["status"] = "blocked"
    app["units"]["hexanator/0"]["workload-status"]["info"] = "small problem"

    kwargs["apps"] = ["hexanator"]
    kwargs["raise_on_blocked"] = True

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert isinstance(idle, JujuUnitError)
    assert isinstance(legacy, JujuUnitError)
    assert "small problem" in str(idle) and "blocked" in str(legacy)


async def test_idle_period(full_status_response: dict, kwargs: dict):
    earlier = datetime.now() - timedelta(seconds=2)
    kwargs["apps"] = ["hexanator"]
    kwargs["idle_period"] = 1
    kwargs["idle_times"] = {"hexanator/0": earlier}

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_unit_idle_timer(full_status_response: dict, kwargs: dict):
    idle, legacy = await model_fake(full_status_response).check_both(
        **{
            **kwargs,
            "apps": ["hexanator"],
            "idle_period": 1,
            "wait_for_at_least_units": 1,
    })
    assert not idle and not legacy


async def test_zero_idle_time(full_status_response: dict, kwargs: dict):
    """Taken from nginx-ingress-integrator-operator integration tests."""
    app = full_status_response["response"]["applications"]["hexanator"]
    app["status"]["status"] = "maintenance"
    app["units"]["hexanator/0"]["workload-status"]["status"] = "maintenance"

    kwargs["apps"] = ["hexanator"]
    kwargs["status"] = "maintenance"
    kwargs["idle_period"] = 0

    idle, legacy = await model_fake(full_status_response).check_both(**kwargs)
    assert idle and legacy


async def test_nonzero_idle_time(full_status_response: dict, kwargs: dict):
    idle, legacy = await model_fake(full_status_response).check_both(
        **{
            **kwargs,
            "apps": ["hexanator"],
            "idle_period": 1,
    })
    assert not idle and not legacy


@pytest.fixture
def kwargs() -> Dict[str, Any]:
    return dict(
        apps=["hexanator", "grafana-agent-k8s", "mysql-test-app"],
        raise_on_error=False,
        raise_on_blocked=False,
        status=None,
        wait_for_at_least_units=None,
        wait_for_exact_units=None,
        timeout=100,
        idle_period=0,
        _wait_for_units=1,
        idle_times={},
        units_ready=set(),
        last_log_time=[None],
        start_time=datetime.now(),
    )


@pytest.fixture
def full_status_response(pytestconfig: pytest.Config) -> dict:
    return json.loads(((pytestconfig.rootpath / "fullstatus.json")).read_text())


def model_fake(resp: dict) -> ModelFake:
    m = ModelFake()
    m._response = resp

    fs = _convert_response(resp, cls=FullStatus)
    assert fs.applications

    for name in fs.applications:
        app = m._applications[name] = ApplicationFake(name, m)

        fsapp = fs.applications[name]
        assert fsapp
        assert fsapp.status  # DetailedStatus
        assert isinstance(fsapp.status.status, str)
        assert isinstance(fsapp.status.info, str)
        app.set_status(fsapp.status.status, fsapp.status.info)

        for uname in fsapp.units:
            app._units.append(unit := UnitFake(uname, m))

            fsunit = fsapp.units[uname]
            assert fsunit

            assert fsunit.agent_status  # DetailedStatus
            assert isinstance(fsunit.agent_status.status, str)
            unit._agent_status = fsunit.agent_status.status

            assert isinstance(fsunit.agent_status.info, str)
            unit._agent_status_message = fsunit.agent_status.info

            assert fsunit.workload_status  # DetailedStatus
            assert isinstance(fsunit.workload_status.status, str)
            unit._workload_status = fsunit.workload_status.status

            assert isinstance(fsunit.machine, str)
            unit._machine_id = fsunit.machine

            assert isinstance(fsunit.workload_status.info, str)
            unit._workload_status_message = fsunit.workload_status.info

    for name, machine in fs.machines.items():
        mac = m._machines[name] = MachineFake(name, m)
        mac._id = name
        assert machine
        assert machine.instance_status
        assert isinstance(machine.instance_status.status, str)
        mac._status = machine.instance_status.status

    return m

class ModelFake(Model):
    _applications: Dict[str, Application]
    _machines: Dict[str, Machine]
    _response: Dict

    async def check_both(self, **kwargs) -> Tuple[Union[bool, Exception], Union[bool, Exception]]:
        idle: Union[bool, Exception]
        legacy: Union[bool, Exception]
        try:
            idle = await self._check_idle(**kwargs)
        except Exception as e:
            idle = e

        try:
            legacy = await self._legacy_check_idle(**kwargs)
        except Exception as e:
            legacy = e

        return idle, legacy

    @property
    def applications(self) -> Dict[str, Application]:
        return self._applications

    @property
    def machines(self) -> Dict[str, Machine]:
        return self._machines

    def __init__(self):
        super().__init__()
        self._applications = {}
        self._machines = {}

    def connection(self):
        rv = Mock()
        rv.facades = {"Client": 6}  # Must match juju.client.connection.client_facades
        rv.rpc = self.rpc
        return rv

    async def rpc(self, msg, encoder=None):
        return self._response


class ApplicationFake(Application):
    _safe_data: dict
    _units: List[Unit]

    def set_status(self, status="fixme", info="some info"):
        self._safe_data["status"]["current"] = status
        self._safe_data["status"]["message"] = info

    @property
    def units(self) -> List[Unit]:
        return self._units

    @property
    def safe_data(self) -> dict:
        return self._safe_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._units = []
        self._safe_data = {"status": {"current": "fixme", "message": "fixme"}}


class UnitFake(Unit):
    _agent_status: str = ""
    _agent_status_message: str = ""
    _workload_status: str = ""
    _workload_status_message: str = ""
    _machine_id: str = ""

    @property
    def agent_status(self) -> str:
        return self._agent_status

    @property
    def agent_status_message(self) -> str:
        return self._agent_status_message

    @property
    def workload_status(self) -> str:
        return self._workload_status

    @property
    def workload_status_message(self) -> str:
        return self._workload_status_message

    @property
    def machine(self) -> Optional[Machine]:
        return self.model.machines.get(self._machine_id)


class MachineFake(Machine):
    _status: str = ""
    _id: str = ""


    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> str:
        return self._status


async def test_model_fake(full_status_response):
    """Self-test for model_fake helper"""
    m = model_fake(full_status_response)

    app = m._applications["hexanator"]
    assert len(app._units) == 1

    u = app._units[0]
    assert u._agent_status == "idle"
    assert not u._agent_status_message
    assert u._workload_status == "active"
    assert not u._workload_status_message

    app = m._applications["grafana-agent-k8s"]
    assert len(app._units) == 1

    u = app._units[0]
    assert u._agent_status == "idle"
    assert not u._agent_status_message
    assert u._workload_status == "blocked"
    assert u._workload_status_message.startswith("Missing incoming")


    app = m._applications["mysql-test-app"]
    assert len(app._units) == 2

    u = [u for u in app._units if u.name.endswith("/0")][0]
    assert u._agent_status == "idle"
    assert not u._agent_status_message
    assert u._workload_status == "waiting"
    assert not u._workload_status_message

    u = [u for u in app._units if u.name.endswith("/1")][0]
    assert u._agent_status == "idle"
    assert not u._agent_status_message
    assert u._workload_status == "waiting"
    assert not u._workload_status_message
