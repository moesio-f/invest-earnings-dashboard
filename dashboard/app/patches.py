"""Patches para bibliotecas externas."""

import logging

logger = logging.getLogger(__name__)


class ObservableDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observers = []

    def add_observer(self, callback):
        self._observers.append(callback)

    def _notify(self, key, value):
        for observer in self._observers:
            observer(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._notify(key, value)


def apply_streamlit_patches():
    def _propagate_logs(
        key,
        value,
    ):
        if isinstance(value, logging.Logger):
            value.propagate = True

    import streamlit as st

    # Create dictionary with callback
    loggers = ObservableDict()
    loggers.add_observer(_propagate_logs)

    # Add current loggers to new dict
    for k, v in st.logger._loggers.items():
        loggers[k] = v

    # Update hidden module registry
    st.logger._loggers = loggers
