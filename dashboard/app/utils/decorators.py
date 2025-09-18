"""Decoradores com funções utilitárias."""

from typing import Callable
import functools
import logging


def log_exceptions(logger: logging.Logger | None = None):
    """Decorador que realiza o log de todas exceções
    de uma função.

    Args:
        logger: logger a ser utilizado.

    Returns:
        Callable: decorador que realiza
            o log de exceções usando
            o logger passado.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                logger.exception(f"{fn.__name__} failed: {e}", exc_info=True)
                raise

        return wrapper

    return decorator
