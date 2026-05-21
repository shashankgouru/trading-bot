# bot/orders.py
# -------------------------------------------------------
# Order Placement Layer for the Trading Bot
# -------------------------------------------------------
# This module handles all order placement logic.
# It sits between the CLI layer and the API client layer.
#
# Responsibilities:
#   - Accept validated inputs from validators.py
#   - Build correct parameters for each order type
#   - Place MARKET and LIMIT orders via the Binance client
#   - Log full request and response details
#   - Return a clean result dictionary to the CLI
#   - Handle and log Binance API errors gracefully
#
# This module never validates inputs itself — that is
# always done by validators.py before calling here.
# -------------------------------------------------------

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException

from bot.logging_config import get_logger

# Get a named logger for this module
logger = get_logger(__name__)


def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None
) -> dict:
    """
    Places a MARKET or LIMIT order on Binance Futures Testnet.

    This is the main function called by cli.py after validation.
    It delegates to the appropriate handler based on order_type.

    Args:
        client:     Authenticated Binance client from client.py
        symbol:     Validated trading pair e.g. "BTCUSDT"
        side:       Validated side e.g. "BUY" or "SELL"
        order_type: Validated type e.g. "MARKET" or "LIMIT"
        quantity:   Validated quantity e.g. 0.001
        price:      Validated price (required for LIMIT) e.g. 50000.0

    Returns:
        Dictionary with clean order result:
        {
            "order_id":     123456789,
            "symbol":       "BTCUSDT",
            "side":         "BUY",
            "type":         "MARKET",
            "quantity":     "0.001",
            "status":       "FILLED",
            "executed_qty": "0.001",
            "avg_price":    "50000.00",
            "raw":          { ...full Binance response... }
        }

    Raises:
        BinanceAPIException:   If Binance rejects the order
        BinanceOrderException: If order parameters are invalid
        Exception:             For unexpected errors
    """

    # Route to the correct handler based on order type
    if order_type == "MARKET":
        return _place_market_order(client, symbol, side, quantity)
    elif order_type == "LIMIT":
        return _place_limit_order(client, symbol, side, quantity, price)


def _place_market_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float
) -> dict:
    """
    Places a MARKET order on Binance Futures Testnet.

    MARKET orders execute immediately at the current market price.
    No price parameter is needed — Binance determines the price.

    Args:
        client:   Authenticated Binance client
        symbol:   Trading pair e.g. "BTCUSDT"
        side:     "BUY" or "SELL"
        quantity: Amount to trade e.g. 0.001

    Returns:
        Clean result dictionary (see place_order docstring)
    """

    # Build the order parameters
    # These are the exact fields Binance Futures API expects
    params = {
        "symbol":   symbol,
        "side":     side,
        "type":     "MARKET",
        "quantity": quantity,
    }

    logger.info(f"Placing MARKET order | {side} {quantity} {symbol}")
    logger.debug(f"MARKET order request params: {params}")

    try:
        # Place the order using python-binance
        # futures_create_order() calls POST /fapi/v1/order
        response = client.futures_create_order(**params)

        logger.debug(f"MARKET order raw response: {response}")
        logger.info(
            f"MARKET order placed successfully | "
            f"OrderId: {response.get('orderId')} | "
            f"Status: {response.get('status')}"
        )

        # Parse and return a clean result
        return _parse_order_response(response)

    except BinanceAPIException as e:
        logger.error(
            f"Binance API error placing MARKET order: "
            f"[{e.status_code}] {e.message}"
        )
        raise

    except BinanceOrderException as e:
        logger.error(
            f"Binance order error placing MARKET order: "
            f"[{e.status_code}] {e.message}"
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error placing MARKET order: {e}")
        raise


def _place_limit_order(
    client: Client,
    symbol: str,
    side: str,
    quantity: float,
    price: float
) -> dict:
    """
    Places a LIMIT order on Binance Futures Testnet.

    LIMIT orders execute only when the market reaches the
    specified price. They stay open until filled or cancelled.

    Args:
        client:   Authenticated Binance client
        symbol:   Trading pair e.g. "BTCUSDT"
        side:     "BUY" or "SELL"
        quantity: Amount to trade e.g. 0.001
        price:    Target price e.g. 50000.0

    Returns:
        Clean result dictionary (see place_order docstring)
    """

    # Build the order parameters
    # timeInForce="GTC" means "Good Till Cancelled"
    # The order stays open until it fills or you cancel it
    # This is required for all LIMIT orders on Binance Futures
    params = {
        "symbol":      symbol,
        "side":        side,
        "type":        "LIMIT",
        "quantity":    quantity,
        "price":       price,
        "timeInForce": "GTC",   # Good Till Cancelled
    }

    logger.info(
        f"Placing LIMIT order | {side} {quantity} {symbol} @ {price}"
    )
    logger.debug(f"LIMIT order request params: {params}")

    try:
        # Place the order using python-binance
        response = client.futures_create_order(**params)

        logger.debug(f"LIMIT order raw response: {response}")
        logger.info(
            f"LIMIT order placed successfully | "
            f"OrderId: {response.get('orderId')} | "
            f"Status: {response.get('status')}"
        )

        # Parse and return a clean result
        return _parse_order_response(response)

    except BinanceAPIException as e:
        logger.error(
            f"Binance API error placing LIMIT order: "
            f"[{e.status_code}] {e.message}"
        )
        raise

    except BinanceOrderException as e:
        logger.error(
            f"Binance order error placing LIMIT order: "
            f"[{e.status_code}] {e.message}"
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error placing LIMIT order: {e}")
        raise


def _parse_order_response(response: dict) -> dict:
    """
    Parses the raw Binance API response into a clean dictionary.

    Binance returns many fields we don't need. This function
    extracts only the important ones for display in the CLI.

    Raw Binance response fields we care about:
      - orderId:      Unique order ID
      - symbol:       Trading pair
      - side:         BUY or SELL
      - type:         MARKET or LIMIT
      - origQty:      Original requested quantity
      - status:       NEW / FILLED / PARTIALLY_FILLED etc.
      - executedQty:  How much was actually filled
      - avgPrice:     Average fill price (0 if not filled yet)

    Args:
        response: Raw dictionary from Binance API

    Returns:
        Clean dictionary with only the important fields
    """
    return {
        # Unique identifier for this order
        "order_id": response.get("orderId"),

        # Trading pair
        "symbol": response.get("symbol"),

        # BUY or SELL
        "side": response.get("side"),

        # MARKET or LIMIT
        "type": response.get("type"),

        # Original requested quantity
        "quantity": response.get("origQty"),

        # Current order status
        # MARKET orders are usually instantly FILLED
        # LIMIT orders start as NEW and fill later
        "status": response.get("status"),

        # How much has been executed so far
        "executed_qty": response.get("executedQty"),

        # Average fill price
        # For MARKET: the actual execution price
        # For LIMIT: 0.00 until the order fills
        "avg_price": response.get("avgPrice"),

        # Keep the full raw response for logging/debugging
        "raw": response,
    }