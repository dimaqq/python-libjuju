# Copyright 2024 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
from __future__ import annotations

import asyncio
import dataclasses
import functools
import logging
import threading
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Optional,
    Self,
    TypeVar,
)

import juju.client.connection
import juju.model

R = TypeVar("R")


@dataclasses.dataclass
class SyncCacheLine(Generic[R]):
    value: Optional[R]
    exception: Optional[Exception]


def cache_until_await(f: Callable[..., R]) -> Callable[..., R]:
    @functools.wraps(f)
    def inner(self: juju.model.ModelEntity, *args, **kwargs) -> R:
        try:
            assert isinstance(self, juju.model.ModelEntity)
            cached: SyncCacheLine[R] = self._sync_cache.setdefault(
                f.__name__,
                SyncCacheLine(None, None),
            )

            if cached.value is None and cached.exception is None:
                asyncio.get_running_loop().call_soon(self._sync_cache.clear)
                try:
                    cached.value = f(self, *args, **kwargs)
                except Exception as e:
                    cached.exception = e

            if cached.exception:
                raise cached.exception

            assert cached.value is not None
            return cached.value
        except AttributeError as e:
            # The decorated functions are commonly used in @property's
            # where the class or base class declares __getattr__ too.
            # Python data model has is that AttributeError is special
            # in this case, so wrap it into something else.
            raise Exception(repr(e)) from e

    return inner


class ThreadedAsyncRunner(threading.Thread):
    _conn: juju.client.connection.Connection | None
    _loop: asyncio.AbstractEventLoop

    @classmethod
    def new_connected(cls, *, connection_kwargs: Dict[str, Any]) -> Self:
        rv = cls()
        rv.start()
        try:
            rv._conn = asyncio.run_coroutine_threadsafe(
                    juju.client.connection.Connection.connect(**connection_kwargs),  # type: ignore[reportUnknownMemberType]
                rv._loop,
            ).result()
            return rv
        except Exception:
            logging.exception("Helper thread failed to connect")
            # TODO: .stop vs .close
            rv._loop.stop()
            rv.join()
            raise

    def call(self, coro: Coroutine[None, None, R]) -> R:
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def stop(self) -> None:
        if self._conn:
            self.call(self._conn.close())
            self._conn = None
        self._loop.call_soon_threadsafe(self._loop.stop)
        self.join()

    @property
    def connection(self) -> juju.client.connection.Connection:
        assert self._conn
        return self._conn

    def __init__(self) -> None:
        super().__init__()
        self._conn = None
        self._loop = asyncio.new_event_loop()

    def run(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
        self._loop.close()
