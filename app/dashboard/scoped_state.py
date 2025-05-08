"""Classe para gerenciamento
de estados com escopos.
"""

from __future__ import annotations

import streamlit as st


class ProxiedGlobal:
    def __init__(self, key: str):
        self._key = key

    def __call__(self):
        return st.session_state[self._key]


class ScopedState:
    def __init__(self, scope: str):
        self.scope = f"state_manager.{scope}"
        if self.scope not in st.session_state:
            st.session_state[self.scope] = dict()

    def get(self, key, default=None):
        return self[key] if key in self else default

    def items(self) -> list[tuple]:
        return list((k, self[k]) for k in self)

    def clear(self):
        st.session_state[self.scope] = dict()

    def __getitem__(self, key):
        return st.session_state[self.scope][key]

    def __getattr__(self, key):
        if key == "scope":
            return super().__getattr__(key)

        return self[key]

    def __setitem__(self, key, value):
        if key == "scope":
            super().__setattr__(key, value)
        else:
            st.session_state[self.scope][key] = value

    def __setattr__(self, key, value):
        self[key] = value

    def __iter__(self):
        for k in st.session_state[self.scope]:
            yield k

    def __delitem__(self, key):
        del st.session_state[self.scope][key]

    def __contains__(self, key) -> bool:
        return key in st.session_state[self.scope]

    @classmethod
    def exists(cls, scope: str) -> bool:
        return scope in st.session_state

    @classmethod
    def clear_scopes(
        cls, keep: str | list[str] = None, keep_no_initialize: bool = False
    ):
        if keep is None:
            keep = []

        if isinstance(keep, str):
            keep = [keep]

        for k in st.session_state:
            if "state_manager." in k:
                if not any(name in k for name in keep):
                    has_initialize = any(
                        "initialized" in item for item in st.session_state[k]
                    )
                    if has_initialize or not keep_no_initialize:
                        del st.session_state[k]
