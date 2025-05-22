from dotenv import load_dotenv, get_key
import sys
from loguru import logger

load_dotenv()
# Configure logger
LOG_LEVEL = get_key(".env", "LOG_LEVEL")

# Remove default handler
logger.remove()

# Add custom handler with formatting
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
)

# Add file logging
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function} - {message}",
    level=LOG_LEVEL,
)

def get_logger(name: str):
    """Get a logger with the given name."""
    return logger.bind(name=name) 