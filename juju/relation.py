# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

import logging
import warnings
from typing import TYPE_CHECKING, Any

from . import model
from .errors import JujuEntityNotFoundError

if TYPE_CHECKING:
    from .application import Application
    from .client._definitions import EndpointStatus, RelationStatus
    from .model import Model

log = logging.getLogger(__name__)

"""
Sample relation from FullStatus

{
    "id": 1,
    "key": "ntp:juju-info ubuntu:juju-info",
    "interface": "juju-info",
    "scope": "container",
    "endpoints": [
        {
            "application": "ubuntu",
            "name": "juju-info",
            "role": "provider",
            "subordinate": false
        },
        {
            "application": "ntp",
            "name": "juju-info",
            "role": "requirer",
            "subordinate": true
        }
    ],
    "status": {
        "status": "joined",
        "info": "",
        "data": {},
        "since": "2024-12-04T01:43:53.72325443Z",
        "kind": "",
        "version": "",
        "life": ""
    }
}
"""


class Endpoint:
    model: Model

    def __init__(self, model, data, relation_id: int, role: str):
        self.model = model
        self.data = data
        self._relation_id = relation_id
        self._role = role

    def _this_endpoint(self) -> EndpointStatus:
        for rel in self.model._full_status().relations:
            assert rel
            if rel.id_ != self._relation_id:
                continue
            for ep in rel.endpoints:
                assert ep
                if ep.role == self._role:
                    return ep
        raise RuntimeError(f"{self} not found")

    def __str__(self) -> str:
        return f"<Endpoint {self._relation_id=} {self._role=}>"

    def __repr__(self) -> str:
        return f"<Endpoint {self._relation_id=} {self._role=} {self.application_name=} {self.name=}>"
        # legacy:
        # return "<Endpoint {}:{}>".format(self.data["application-name"], self.name)

    @property
    def application_name(self) -> str:
        rv = self._this_endpoint().application
        self._validate_legacy(rv, key=["application-name"])
        assert isinstance(rv, str)
        return rv

    def _validate_legacy(self, new: Any, *, key: list[str]) -> None:
        if self.data is model.JUJU4_NO_SAFE_DATA:
            return
        legacy = self.data
        for k in key:
            legacy = legacy[k]
        if new != legacy:
            warnings.warn(f"Endpoint {key} mismatch {new=} {legacy=}", stacklevel=3)

    @property
    def application(self) -> Application:
        """Application returns the underlying application model from the state.
        If no application is found, then a JujuEntityNotFoundError is raised, in
        this scenario it is expected that you disconnect and reconnect to the
        model.
        """
        app_name = self.application_name
        if app_name in self.model.applications:
            return self.model.applications[app_name]
        raise JujuEntityNotFoundError(app_name, ["application"])

    @property
    def name(self) -> str:
        rv = self._this_endpoint().name
        self._validate_legacy(rv, key=["relation", "name"])
        assert isinstance(rv, str)
        return rv

    @property
    def interface(self) -> str:
        rv = self.model.relations[self._relation_id]._interface()
        self._validate_legacy(rv, key=["relation", "interface"])
        return rv

    @property
    def role(self) -> str:
        rv = self._this_endpoint().role
        self._validate_legacy(rv, key=["relation", "role"])
        assert isinstance(rv, str)
        return rv

    @property
    def scope(self):
        rv = self.model.relations[self._relation_id]._scope()
        self._validate_legacy(rv, key=["relation", "scope"])
        return rv


class Relation(model.ModelEntity):
    def __repr__(self):
        return f"<Relation id={self.entity_id}"
        # FIXME cannot use key here unless stamped at __init__ time
        # return f"<Relation id={self.entity_id} {self.key}>"

    def _this_relation(self) -> RelationStatus:
        for rel in self.model._full_status():
            assert rel
            if rel.id_ != self._relation_id:
                continue
            return rel
        raise RuntimeError(f"{self} not found")

    def _interface(self) -> str: ...

    def _scope(self) -> str: ...

    @property
    def endpoints(self) -> list[Endpoint]:
        if self.safe_data is model.JUJU4_NO_SAFE_DATA:
            rv = []
            for ep in self._this_relation().endpoints:
                assert ep
                assert isinstance(ep.role, str)
                rv.append(
                    Endpoint(
                        self.model,
                        model.JUJU4_NO_SAFE_DATA,
                        int(self.entity_id),
                        ep.role,
                    )
                )
            return rv

        # FIXME how to validate that the above and this are the same set of endpoints?
        return [
            Endpoint(self.model, data, int(self.entity_id), data["relation"]["role"])
            for data in self.safe_data["endpoints"]
        ]

    @property
    def provides(self) -> Endpoint | None:
        """The endpoint on the provides side of this relation, or None."""
        for endpoint in self.endpoints:
            if endpoint.role == "provider":
                return endpoint
        return None

    @property
    def requires(self) -> Endpoint | None:
        """The endpoint on the requires side of this relation, or None."""
        for endpoint in self.endpoints:
            if endpoint.role == "requirer":
                return endpoint
        return None

    @property
    def peers(self) -> Endpoint | None:
        """The peers endpoint of this relation, or None."""
        for endpoint in self.endpoints:
            if endpoint.role == "peer":
                return endpoint
        return None

    @property
    def is_subordinate(self) -> bool:
        return any(ep.scope == "container" for ep in self.endpoints)

    @property
    def is_peer(self) -> bool:
        return any(ep.role == "peer" for ep in self.endpoints)

    def matches(self, *specs):
        """Check if this relation matches relationship specs.

        Relation specs are strings that would be given to Juju to establish a
        relation, and should be in the form ``<application>[:<endpoint_name>]``
        where the ``:<endpoint_name>`` suffix is optional.  If the suffix is
        omitted, this relation will match on any endpoint as long as the given
        application is involved.

        In other words, this relation will match a spec if that spec could have
        created this relation.

        :return: True if all specs match.
        """

        # Matches expects that the underlying application exists when it walks
        # over the endpoints.
        # This isn't directly required, but it validates that the framework
        # has all the information available to it, when you walk over all the
        # relations.
        # The one exception is remote-<uuid> applications aren't real
        # applications in the general sense of a application, but are more akin
        # to a shadow application.
        def model_application_exists(app_name):
            model_app_name = None
            if app_name in self.model.applications:
                model_app_name = self.model.applications[app_name].name
            elif app_name in self.model.remote_applications:
                model_app_name = self.model.remote_applications[app_name].name
            elif app_name in self.model.application_offers:
                model_app_name = self.model.application_offers[app_name].name
            return model_app_name == app_name

        for spec in specs:
            if ":" in spec:
                app_name, endpoint_name = spec.split(":")
            else:
                app_name, endpoint_name = spec, None
            for endpoint in self.endpoints:
                if (
                    app_name == endpoint.application_name
                    and model_application_exists(app_name)
                    and endpoint_name in (endpoint.name, None)
                ):
                    # found a match for this spec, so move to next one
                    break
            else:
                # no match for this spec
                return False
        return True

    @property
    def applications(self):
        """All applications involved in this relation."""
        return [ep.application for ep in self.endpoints]
