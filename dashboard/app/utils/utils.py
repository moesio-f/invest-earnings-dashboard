"""Utilidades para a UI como um todo."""

from app.utils.state import ScopedState
from app.utils.state.proxies import StateProxy


def safe_get_from_proxied_data(scope: ScopedState, key: str, default=None):
    maybe_proxy = scope.get(key, None)
    if isinstance(maybe_proxy, StateProxy):
        return maybe_proxy.get(default)
    elif maybe_proxy is None:
        maybe_proxy = default
    return maybe_proxy
