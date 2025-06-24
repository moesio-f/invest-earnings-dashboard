"""Entrypoint do processador de YoC."""

from .config import YoCProcessorConfig
from .processor import YoCProcessor

# Get configuration
config = YoCProcessorConfig()

# Create processor
processor = YoCProcessor(
    config.yoc_queue,
    config.broker_url,
    config.wallet_db_url,
    config.analytic_db_url,
    config.temperature,
)

# Start processor
processor.run()
