"""Classe para gerenciamento de
estados.
"""

import streamlit as st
from app.utils.state.proxies import ProxiedGlobal
from app.utils.state.scoped_state import ScopedState


class _StateManager:
    """Gerenciador de estados.

    Essa classe permite o gerenciamento de
    escopos. O streamlit provê formas de armazenar
    estados em um dicionário global, essa classe
    permite limitar o escopo de acesso aos atributos
    dessa classe.
    """

    _REGISTRY_KEY: str = "__SM_Registry"
    _PAGE_PREFIX: str = "__SM_Page"
    _DATA_PREFIX: str = "__SM_Data"

    def __init__(self):
        # Get registry from session state or default
        self._registry: dict[str, dict[str, str]] = st.session_state.get(
            self._REGISTRY_KEY, dict(pages=dict(), data=dict())
        )

        # Guarantee it is saved on session
        st.session_state[self._REGISTRY_KEY] = self._registry

    def get_page_state(self, name: str) -> ScopedState:
        """Retorna um escopo para ser utilizado para
        armazenamento de dados de uma página.

        :param name: nome da página.
        :return: escopo de leitura e escrita.
        """
        return self._get_state("pages", name)

    def get_data_state(self, name: str) -> ScopedState:
        """Retorna um escopo para ser utilizado
        para armazenamento de dados.

        :param name: nome do conjunto de dados.
        :return: escopo de leitura e escrita.
        """
        return self._get_state("data", name)

    def get_proxied_data_state(self, name: str, prefix: str) -> ScopedState:
        """Retorna um escopo de dados inicializado a partir
        de chaves presentes em `streamlit.session_state`.

        Esse escopo deve ser utilizado apenas para leitura.

        :param name: nome do escopo.
        :param prefix: prefixo das chaves a serem lidas do estado
            global do streamlit.
        :return: escopo para leitura.
        """
        state = self.get_data_state(name)

        if not prefix.endswith("_"):
            prefix += "_"

        for k in st.session_state:
            if k.startswith(prefix):
                attr_name = k.replace(prefix, "")
                state[attr_name] = ProxiedGlobal(k)

        return state

    def exists_page(self, page: str) -> bool:
        return page in self._registry

    def clear_pages(self, destroy: bool = True, keep: str | list[str] = None):
        self._clear_reg("pages", destroy, keep)

    def clear_data(self, destroy: bool = True, keep: str | list[str] = None):
        self._clear_reg("data", destroy, keep)

    def _get_state(self, reg_key: str, name: str) -> ScopedState:
        # Maybe it's empty?
        if name not in self._registry[reg_key]:
            scope = f"{self._PAGE_PREFIX}_{name.replace(" ", "_")}"
            self._registry[reg_key][name] = scope

        # Return write/read scope for page
        return ScopedState(self._registry[reg_key][name])

    def _clear_reg(
        self, reg_key: str, destroy: bool = True, keep: str | list[str] = None
    ):
        if keep is None:
            keep = []

        if isinstance(keep, str):
            keep = [keep]

        for k, v in self._registry[reg_key].items():
            v = ScopedState(v)
            if k not in keep:
                if destroy:
                    v.remove()
                else:
                    v.clear()


Manager = _StateManager()
