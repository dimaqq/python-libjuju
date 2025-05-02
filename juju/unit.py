# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging
import warnings
from typing import Any, List, Optional

from juju.errors import JujuError
from juju.machine import Machine

from . import model, tag
from .annotationhelper import _get_annotations, _set_annotations
from .client import client
from .client._definitions import (
    UnitStatus,
)

log = logging.getLogger(__name__)


class Unit(model.ModelEntity):
    @property
    def name(self) -> str:
        return self.entity_id

    @property
    def _unit_status(self) -> UnitStatus:
        app = self.name.split("/")[0]
        return model._idle.app_units(self.model._full_status(), app)[self.entity_id]

    def _validate_legacy(self, new: Any, *, key: List[str]) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=model.LegacyWarning)
            if self.safe_data is model.JUJU4_NO_SAFE_DATA:
                return
            legacy = self.safe_data
            for k in key:
                legacy = legacy[k]
            if new != legacy:
                warnings.warn(f"Unit {key} mismatch {new=} {legacy=}", stacklevel=3)

    @property
    def agent_status(self) -> str:
        """Returns the current agent status string."""
        assert self._unit_status.agent_status
        rv = self._unit_status.agent_status.status
        self._validate_legacy(rv, key=["agent-status", "current"])
        assert isinstance(rv, str)
        return rv

    @property
    def agent_status_since(self) -> str:
        """Get the time when the `agent_status` was last updated."""
        assert self._unit_status.agent_status
        rv = self._unit_status.agent_status.since
        self._validate_legacy(rv, key=["agent-status", "since"])
        assert isinstance(rv, str)
        return rv

    @property
    def is_subordinate(self) -> bool:
        """True if the unit is subordinate of another unit"""
        rv = False
        for app in self.model._full_status().applications.values():
            assert app
            for unit in app.units.values():
                assert unit
                if self.entity_id in unit.subordinates:
                    rv = True
        self._validate_legacy(rv, key=["subordinate"])
        return rv

    @property
    def principal_unit(self) -> str:
        """Returns the name of the unit of which this unit is a subordinate to.
        Returns '' for principal units themselves.
        """
        rv = ""
        for app in self.model._full_status().applications.values():
            assert app
            for unit_name, unit in app.units.items():
                assert unit
                if self.entity_id in unit.subordinates:
                    rv = unit_name
        self._validate_legacy(rv, key=["principal"])
        return rv

    @property
    def agent_status_message(self) -> str:
        """Get the agent status message."""
        assert self._unit_status.agent_status
        rv = self._unit_status.agent_status.info
        self._validate_legacy(rv, key=["agent-status", "message"])
        assert isinstance(rv, str)
        return rv

    @property
    def workload_status(self):
        """Returns the current workload status string."""
        assert self._unit_status.workload_status
        rv = self._unit_status.workload_status.status
        self._validate_legacy(rv, key=["workload-status", "current"])
        assert isinstance(rv, str)
        return rv

    @property
    def workload_status_since(self) -> str:
        """Get the time when the `workload_status` was last updated."""
        assert self._unit_status.workload_status
        rv = self._unit_status.workload_status.since
        self._validate_legacy(rv, key=["workload-status", "since"])
        assert isinstance(rv, str)
        return rv

    @property
    def workload_status_message(self):
        """Get the workload status message."""
        assert self._unit_status.workload_status
        rv = self._unit_status.workload_status.info
        self._validate_legacy(rv, key=["workload-status", "message"])
        assert isinstance(rv, str)
        return rv

    def _machine_id(self) -> str:
        # k8s: the machine field is always an empty string
        # vms: the field is an empty string for the nested, subordinate unit status
        #      it is, however, set on the main unit statu
        if goto := self.principal_unit:
            return self.model.units[goto]._machine_id()
        rv = self._unit_status.machine
        assert isinstance(rv, str)
        return rv

    @property
    def machine(self) -> Optional[Machine]:
        """Get the machine object for this unit."""
        machine_id = self._machine_id()
        self._validate_legacy(machine_id, key=["machine-id"])
        if machine_id:
            return self.model.machines.get(machine_id, None)
        else:
            return None

    @property
    def public_address(self) -> Optional[str]:
        """Get the public address.

        FICME: not so deprecated?
        This property is deprecated, use get_public_address method.
        """
        rv = self._unit_status.public_address
        self._validate_legacy(rv, key=["public-address"])
        assert isinstance(rv, (str, type(None)))
        return rv or None

    @property
    def tag(self):
        return tag.unit(self.name)

    def get_subordinates(self):
        """Returns the unit objects that are subordinates to this unit

        :return [Unit]
        """
        return [
            u for u in self.model.units.values() if u.principal_unit == self.entity_id
        ]

    async def destroy(
        self, destroy_storage=False, dry_run=False, force=False, max_wait=None
    ):
        """Destroy this unit."""
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug("Destroying %s", self.name)

        return await app_facade.DestroyUnit(
            units=[
                {
                    "unit-tag": self.tag,
                    "destroy-storage": destroy_storage,
                    "force": force,
                    "max-wait": max_wait,
                    "dry-run": dry_run,
                }
            ]
        )

    remove = destroy

    async def get_public_address(self):
        """Return the public address of this unit.

        :return int public-address
        """
        # FIXME: if we're getting the latest FullStatus, can I rely on the data?
        return self.public_address

        # addr = self.safe_data["public-address"] or None
        # if addr is not None:
        #     return addr

        # app_facade = client.ApplicationFacade.from_connection(self.connection)
        # def_result = await app_facade.UnitsInfo(entities=[client.Entity(self.tag)])
        # if def_result is not None and len(def_result.results) > 1:
        #     raise JujuAPIError("expected one result")
        # return def_result.results[0].result.get("public-address", None)

    async def resolved(self, retry=False):
        """Mark unit errors resolved.

        :param bool retry: Re-execute failed hooks
        :returns: A :class:`juju.client._definitions.ErrorResults` instance.
        """
        app_facade = client.ApplicationFacade.from_connection(self.connection)

        log.debug("Resolving %s", self.name)

        return await app_facade.ResolveUnitErrors(
            all_=False, retry=retry, tags={"entities": [{"tag": self.tag}]}
        )

    async def add_storage(self, storage_name, pool=None, count=1, size=1024):
        """Creates a storage and adds it to this unit.

        :param: str storage_name: Name of the storage
        :param: str pool: the storage pool to provision storage instances from. Must
        be a name from 'juju storage-pools'.  The default pool is available via
        executing 'juju model-config storage-default-block-source'.
        :param: int count: the number of storage instances to provision from <storage-pool> of
        <size>. Must be a positive integer. The default count is "1". May be restricted
        by the charm, which can specify a maximum number of storage instances per unit.
        :param: int size: the required size of the storage instance, in MiB.

        :return: []str storage_tags
        """
        constraints = client.StorageConstraints(count=count, size=size)
        if pool:
            constraints = client.StorageConstraints(pool=pool, count=count, size=size)

        storage_facade = client.StorageFacade.from_connection(self.connection)
        res = await storage_facade.AddToUnit(
            storages=[
                client.StorageAddParams(
                    name=storage_name,
                    unit=self.tag,
                    storage=constraints,
                )
            ]
        )
        result = res.results[0]
        if result.error is not None:
            raise JujuError(f"{result.error}")
        storage_details = result.result
        return storage_details.storage_tags

    async def attach_storage(self, storage_ids=[]):
        """Attaches existing storage to this unit.

        :param [str] storage_ids: existing storage ids to attach to the unit
        :return:
        """
        if not storage_ids:
            raise JujuError(f"Expected a storage ID to be attached to unit {self.name}")

        storage_facade = client.StorageFacade.from_connection(self.connection)
        return await storage_facade.Attach(
            ids=[
                client.StorageAttachmentId(
                    storage_tag=tag.storage(s_id),
                    unit_tag=self.tag,
                )
                for s_id in storage_ids
            ]
        )

    async def detach_storage(self, *storage_ids, force=False):
        """Detaches storage from units.

        :param bool force: Forcefully detach storage
        :param [str] storage_ids:
        :return:
        """
        if not storage_ids:
            raise JujuError("Expected at least one storage ID")

        storage_facade = client.StorageFacade.from_connection(self.connection)
        ret = await storage_facade.DetachStorage(
            force=force,
            ids=client.StorageAttachmentIds(
                ids=[
                    client.StorageAttachmentId(
                        storage_tag=tag.storage(s),
                        unit_tag=self.tag,
                    )
                    for s in storage_ids
                ]
            ),
        )
        if ret.results[0].error:
            raise JujuError(ret.results[0].error.message)

    async def run(self, command, timeout=None, block=False):
        """Run command on this unit.

        :param str command: The command to run
        :param int timeout: Time, in seconds, to wait before command is
        considered failed
        :param bool block: A flag to use this function in synchronized fashion.
        Useful with older versions of juju, i.e. getting the result without
        having to call ``action.wait()`` separately.
        :returns: A :class:`juju.action.Action` instance.

        Note that this is very similarly to unit.run_action only enqueues the action.
        You will need to call ``action.wait()`` on the resulting `Action` instance
        if you wish to block until the action is complete.

        """
        action = client.ActionFacade.from_connection(self.connection)

        log.debug("Running `%s` on %s", command, self.name)

        if timeout:
            # Convert seconds to nanoseconds
            timeout = int(timeout * 1000000000)

        # It's not enough to only check for the old_client on the connection here
        # The old client's ActionFacade is updated to version 7, so
        # 2.9 track client may be using either ActionFacade v6 or v7 too
        old_facade = client.ActionFacade.best_facade_version(self.connection) <= 6

        res = await action.Run(
            applications=[],
            commands=command,
            machines=[],
            timeout=timeout,
            units=[self.name],
        )

        action_result = res.results[0] if old_facade else res.actions[0]
        action = action_result.action

        action_id = action.tag
        if action_id.startswith("action-"):
            # strip the action- part of "action-<num>" tag
            action_id = action_id[7:]

        error = action_result.error
        if error:
            raise JujuError(f"Action error - {error.code} : {error.message}")

        action = await self.model._wait_for_new("action", action_id)
        if block:
            return await action.wait()
        return action

    async def run_action(self, action_name, **params):
        """Run an action on this unit.

        :param str action_name: Name of action to run
        :param **params: Action parameters
        :returns: A :class:`juju.action.Action` instance.

        Note that this only enqueues the action.  You will need to call
        ``action.wait()`` on the resulting `Action` instance if you wish
        to block until the action is complete.

        """
        action_facade = client.ActionFacade.from_connection(self.connection)
        log.debug("Starting action `%s` on %s", action_name, self.name)

        old_client = self.connection.is_using_old_client

        op = action_facade.Enqueue if old_client else action_facade.EnqueueOperation
        res = await op(
            actions=[
                client.Action(
                    name=action_name,
                    parameters=params,
                    receiver=self.tag,
                )
            ]
        )

        _action = res.results[0] if old_client else res.actions[0]
        action = _action.action
        error = _action.error

        if error and error.code == "not found":
            raise ValueError("Action `%s` not found on %s" % (action_name, self.name))
        elif error:
            raise Exception("Unknown action error: %s" % error.serialize())
        action_id = action.tag[len("action-") :]
        log.debug("Action started as %s", action_id)
        # we mustn't use wait_for_action because that blocks until the
        # action is complete, rather than just being in the model
        return await self.model._wait_for_new("action", action_id)

    async def scp_to(
        self, source, destination, user="ubuntu", proxy=False, scp_opts=""
    ):
        """Transfer files to this unit.

        :param str source: Local path of file(s) to transfer
        :param str destination: Remote destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        """
        await self.machine.scp_to(
            source, destination, user=user, proxy=proxy, scp_opts=scp_opts
        )

    async def scp_from(
        self, source, destination, user="ubuntu", proxy=False, scp_opts=""
    ):
        """Transfer files from this unit.

        :param str source: Remote path of file(s) to transfer
        :param str destination: Local destination of transferred files
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param scp_opts: Additional options to the `scp` command
        :type scp_opts: str or list
        """
        await self.machine.scp_from(
            source, destination, user=user, proxy=proxy, scp_opts=scp_opts
        )

    async def ssh(self, command, user="ubuntu", proxy=False, ssh_opts=None):
        """Execute a command over SSH on this unit.

        :param str command: Command to execute
        :param str user: Remote username
        :param bool proxy: Proxy through the Juju API server
        :param str ssh_opts: Additional options to the `ssh` command

        """
        return await self.machine.ssh(command, user, proxy, ssh_opts)

    async def is_leader_from_status(self):
        """Check to see if this unit is the leader. Returns True if so, and
        False if it is not, or if leadership does not make sense
        (e.g., there is no leader in this application.)

        This method is a kluge that calls FullStatus in the
        ClientFacade to get its information. Once
        https://bugs.launchpad.net/juju/+bug/1643691 is resolved, we
        should add a simple .is_leader property, and deprecate this
        method.

        """
        unit_parts = self.name.split("/")
        app = unit_parts[0]

        client_facade = client.ClientFacade.from_connection(self.connection)

        status = await client_facade.FullStatus(patterns=None)
        # FullStatus may be more up to date than our model, and the
        # unit may have gone away, or we may be doing something silly,
        # like trying to fetch leadership for a subordinate, which
        # will not be filed where we expect in the model. In those
        # cases, we may simply return False, as a nonexistent or
        # subordinate unit is not a leader.
        if not status.applications.get(app):
            return False

        # We will attempt to look in two places for a leader property based on
        # if the unit is subordinate or not. These variables allow for more
        # generic non discriminate checks
        target_apps = [app]
        is_subordinate = False

        # Is the application a subordinate? If so change our data variables to
        # the parent
        if status.applications[app].subordinate_to:
            is_subordinate = True
            target_apps = status.applications[app].subordinate_to

        for target_app in target_apps:
            app_data = status.applications[target_app]

            if not app_data.units:
                continue

            if app_data.units.get(self.name):
                is_leader = app_data.units[self.name].leader
                return is_leader if is_leader else False

            if not is_subordinate:
                continue

            for unit in app_data.units.values():
                if unit.subordinates and unit.subordinates.get(self.name):
                    is_leader = unit.subordinates[self.name].leader
                    return is_leader if is_leader else False

        return False

    async def get_metrics(self):
        """Get metrics for the unit.

        :return: Dictionary of metrics for this unit.

        """
        metrics = await self.model.get_metrics(self.tag)
        return metrics[self.name]

    async def get_annotations(self):
        """Get annotations on this unit.

        :return dict: The annotations for this unit
        """
        return await _get_annotations(self.tag, self.connection)

    async def set_annotations(self, annotations):
        """Set annotations on this unit.

        :param annotations map[string]string: the annotations as key/value
            pairs.

        """
        return await _set_annotations(self.tag, annotations, self.connection)
