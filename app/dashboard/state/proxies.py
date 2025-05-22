"""Proxies."""

from typing import Protocol, runtime_checkable

import streamlit as st


@runtime_checkable
class StateProxy(Protocol):
    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs): ...


class ProxiedGlobal(StateProxy):
    def __init__(self, key: str):
        self._key = key

    def get(self, *args, **kwargs):
        # Initial argument is key
        fn_args = [self._key]

        # Has default?
        if (kw_default := kwargs.pop("default", None)) is not None:
            fn_args.append(kw_default)
        elif len(args) == 1:
            fn_args.append(args[0])

        return st.session_state.get(*fn_args)


class ProxiedValue:
    def __init__(self, value):
        self._value = value

    def get(self, *args, **kwargs):
        del args, kwargs
        return self._value
