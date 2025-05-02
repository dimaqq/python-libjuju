# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.

import logging

from . import model

log = logging.getLogger(__name__)


class Annotation(model.ModelEntity):
    # FIXME this is not exposed -- can't get these from the model
    # I think that the class exists only for Deltas to go somewhere
    pass
