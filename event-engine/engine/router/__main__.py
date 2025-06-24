"""Entrypoint do router."""

from .config import RouterConfig
from .router import Router

# Get configuration
config = RouterConfig()

# Create Router
router = Router(config.notification_queue, config.yoc_queue, config.broker_url)

# Start router
router.run()
