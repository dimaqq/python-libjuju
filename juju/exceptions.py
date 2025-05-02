# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.


class DeadEntityException(Exception):
    # FIXME: not used in integration tests or COU
    # pytest-operator references this symbol, so it can't just be removed
    # - in _reset, while destroying the model, this exception is ignored
    pass
