# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
"""Client version definitions."""

LTS_RELEASES = ["noble", "jammy", "focal", "bionic", "xenial", "trusty", "precise"]

SERIES_TO_BASE = {
    "noble": "ubuntu@24.04",
    "jammy": "ubuntu@22.04",
    "focal": "ubuntu@20.04",
    "bionic": "ubuntu@18.04",
    "xenial": "ubuntu@16.04",
    "trusty": "ubuntu@14.04",
    "precise": "ubuntu@12.04",
    "groovy": "ubuntu@20.10",
    "disco": "ubuntu@19.04",
    "cosmic": "ubuntu@18.10",
    "artful": "ubuntu@17.10",
    "vivid": "ubuntu@15.04",
}

DEFAULT_ARCHITECTURE = "amd64"

CLIENT_VERSION = "3.5.2.0"
