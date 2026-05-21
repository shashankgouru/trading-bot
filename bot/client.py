# bot/client.py
# -------------------------------------------------------
# Binance Futures Testnet — API Client Layer
# -------------------------------------------------------
# This module is the ONLY place that directly interacts
# with the python-binance library and Binance's API.
#
# Responsibilities:
#   - Load API credentials from .env file
#   - Create and configure the Binance Futures client
#   - Point the client to the Testnet base URL
#   - Provide a single shared client instance to other modules
#   - Handle connection-level errors cleanly
#
# Every other module gets the client by calling:
#   from bot.client import get_client
# -------------------------------------------------------

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException

from bot.logging_config import get_logger

# Get a named logger for this module
# Log lines will show: "bot.client" as the source
logger = get_logger(__name__)

# -------------------------------------------------------
# Load environment variables from .env file
# -------------------------------------------------------
# load_dotenv() reads the .env file in your project root
# and makes API_KEY and API_SECRET available via os.getenv()
load_dotenv()


def get_client() -> Client:
    """
    Creates and returns a configured Binance client
    pointed at the Futures Testnet.

    Steps:
      1. Reads API_KEY and API_SECRET from .env
      2. Validates they are not empty
      3. Creates a python-binance Client instance
      4. Overrides the base URLs to point at Testnet
      5. Tests the connection with a simple ping
      6. Returns the ready-to-use client

    Returns:
        binance.client.Client: Authenticated Binance client

    Raises:
        ValueError: If API keys are missing from .env
        BinanceAPIException: If Binance rejects the credentials
        ConnectionError: If the Testnet cannot be reached
    """

    # -------------------------------------------------------
    # Step 1: Read API credentials from environment
    # -------------------------------------------------------
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    # -------------------------------------------------------
    # Step 2: Validate credentials exist
    # -------------------------------------------------------
    # getenv() returns None if the variable is missing
    # We check for both None and empty string ""
    if not api_key or not api_secret:
        logger.error("API_KEY or API_SECRET is missing from .env file")
        raise ValueError(
            "API_KEY and API_SECRET must be set in your .env file.\n"
            "Example:\n"
            "  API_KEY=your_key_here\n"
            "  API_SECRET=your_secret_here"
        )

    logger.debug("API credentials loaded successfully from .env")

    # -------------------------------------------------------
    # Step 3: Create the Binance client
    # -------------------------------------------------------
    # testnet=True alone is NOT enough for Futures Testnet
    # We must manually override the API URLs (done in Step 4)
    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=False   # We manually set Futures Testnet URLs below
        )

        # -------------------------------------------------------
        # Step 4: Override URLs to point at Futures Testnet
        # -------------------------------------------------------
        # python-binance defaults to live Binance URLs.
        # We override them to use the Futures Testnet endpoints.
        #
        # API_URL      → used for all REST API calls
        # FUTURES_URL  → used specifically for Futures endpoints
        # -------------------------------------------------------
        testnet_url = "https://testnet.binancefuture.com"

        # Override the base REST API URL
        client.API_URL = testnet_url + "/api"

        # Override the Futures-specific URL
        client.FUTURES_URL = testnet_url + "/fapi"

        logger.debug(f"Client configured for Futures Testnet: {testnet_url}")

        # -------------------------------------------------------
        # Step 5: Test the connection with a lightweight ping
        # -------------------------------------------------------
        # futures_ping() sends a GET /fapi/v1/ping request
        # It returns an empty dict {} on success
        # This confirms the Testnet is reachable and keys work
        client.futures_ping()
        logger.info("Successfully connected to Binance Futures Testnet")

        # -------------------------------------------------------
        # Step 6: Return the ready-to-use client
        # -------------------------------------------------------
        return client

    except BinanceAPIException as e:
        # Binance returned an error response (e.g. invalid API key)
        logger.error(f"Binance API error during client setup: {e.status_code} - {e.message}")
        raise

    except Exception as e:
        # Network issues, timeouts, DNS failures, etc.
        logger.error(f"Unexpected error while connecting to Binance Testnet: {e}")
        raise ConnectionError(
            f"Could not connect to Binance Futures Testnet.\n"
            f"Check your internet connection and API keys.\n"
            f"Details: {e}"
        )