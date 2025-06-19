"""Gerenciador de estado para
páginas da aplicação.
"""

import uuid

from .scoped_state import ScopedState
from .state_manager import Manager


class PageState:
    def __init__(self, page_name: str):
        self._page = page_name
        self._state = Manager.get_page_state(self._page)
        self._component_prefix = str(uuid.uuid4())

    @property
    def variables(self) -> ScopedState:
        return self._state

    @property
    def page(self) -> str:
        return self._page

    @property
    def components(self) -> ScopedState:
        return Manager.get_proxied_data_state(
            f"{self.page}_components", self._component_prefix
        )

    def register_component(self, name: str) -> str:
        return f"{self._component_prefix}_{name}"

    def update_state(self, *args, **kwargs):
        raise NotImplementedError()
