import logging
import sys
from pathlib import Path

# Create logs folder if not exists
Path("logs").mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Show in terminal
        logging.FileHandler("logs/app.log")  # Save to file
    ]
)

logger = logging.getLogger(__name__)
logger.info(" Logging configured successfully!")