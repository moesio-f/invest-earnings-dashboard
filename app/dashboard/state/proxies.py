"""Proxies."""

from typing import Protocol
import streamlit as st


class StateProxy(Protocol):
    def __call__(self):
        return self.get()

    def get(self): ...


class ProxiedGlobal(StateProxy):
    def __init__(self, key: str):
        self._key = key

    def get(self):
        return st.session_state[self._key]


class ProxiedValue:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self._value
