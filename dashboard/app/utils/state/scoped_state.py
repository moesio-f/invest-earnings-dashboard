"""Estados com
escopo.
"""

from __future__ import annotations

import streamlit as st


class ScopedState:
    """Estado com escopo.

    Permite limitar o acesso de leitura e
    escrita no estado global através de um
    escopo.


    :param scope: nome do escopo.
    """

    def __init__(self, scope: str):
        self.scope = scope
        if self.scope not in st.session_state:
            st.session_state[self.scope] = dict()

    def get(self, key, default=None):
        return self[key] if key in self else default

    def keys(self) -> list[str]:
        return list(st.session_state[self.scope])

    def items(self) -> list[tuple]:
        return list((k, self[k]) for k in self)

    def clear(self):
        st.session_state[self.scope] = dict()

    def remove(self):
        self.clear()
        del st.session_state[self.scope]

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
