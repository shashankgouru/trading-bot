# bot/validators.py
# -------------------------------------------------------
# Input Validation Layer for the Trading Bot
# -------------------------------------------------------
# This module validates ALL user inputs before they are
# sent to the Binance API.
#
# Responsibilities:
#   - Validate trading symbol format (e.g. BTCUSDT)
#   - Validate order side (BUY or SELL)
#   - Validate order type (MARKET or LIMIT)
#   - Validate quantity (must be positive number)
#   - Validate price (required for LIMIT, must be positive)
#
# All functions raise ValueError with clear messages on failure.
# They return cleaned/normalized values on success.
# -------------------------------------------------------

from bot.logging_config import get_logger

# Get a named logger for this module
logger = get_logger(__name__)

# -------------------------------------------------------
# Allowed values — defined once, used everywhere
# -------------------------------------------------------
VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT"]


def validate_symbol(symbol: str) -> str:
    """
    Validates and normalizes the trading symbol.

    Rules:
      - Must not be empty
      - Converted to uppercase automatically
      - Must only contain letters (no spaces, numbers, special chars)
      - Common pairs like BTCUSDT, ETHUSDT, BNBUSDT are valid

    Args:
        symbol: Trading pair string e.g. "btcusdt" or "BTCUSDT"

    Returns:
        Uppercase symbol string e.g. "BTCUSDT"

    Raises:
        ValueError: If symbol is empty or contains invalid characters
    """
    # Strip whitespace and convert to uppercase
    symbol = symbol.strip().upper()

    # Check it's not empty after stripping
    if not symbol:
        logger.warning("Validation failed: symbol is empty")
        raise ValueError("Symbol cannot be empty. Example: BTCUSDT")

    # Check it only contains letters (A-Z)
    # Binance futures symbols are always alphabetic e.g. BTCUSDT
    if not symbol.isalpha():
        logger.warning(f"Validation failed: invalid symbol format '{symbol}'")
        raise ValueError(
            f"Invalid symbol '{symbol}'. "
            f"Symbol must contain only letters. Example: BTCUSDT"
        )

    logger.debug(f"Symbol validated: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    """
    Validates the order side.

    Rules:
      - Must be BUY or SELL (case-insensitive)

    Args:
        side: Order side string e.g. "buy" or "BUY"

    Returns:
        Uppercase side string e.g. "BUY"

    Raises:
        ValueError: If side is not BUY or SELL
    """
    # Normalize to uppercase
    side = side.strip().upper()

    if side not in VALID_SIDES:
        logger.warning(f"Validation failed: invalid side '{side}'")
        raise ValueError(
            f"Invalid side '{side}'. "
            f"Must be one of: {', '.join(VALID_SIDES)}"
        )

    logger.debug(f"Side validated: {side}")
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validates the order type.

    Rules:
      - Must be MARKET or LIMIT (case-insensitive)

    Args:
        order_type: Order type string e.g. "market" or "MARKET"

    Returns:
        Uppercase order type string e.g. "MARKET"

    Raises:
        ValueError: If order type is not MARKET or LIMIT
    """
    # Normalize to uppercase
    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        logger.warning(f"Validation failed: invalid order type '{order_type}'")
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )

    logger.debug(f"Order type validated: {order_type}")
    return order_type


def validate_quantity(quantity: float) -> float:
    """
    Validates the order quantity.

    Rules:
      - Must be a positive number
      - Must be greater than zero
      - Binance has minimum quantity requirements per symbol
        (we do basic check here; Binance will reject if too small)

    Args:
        quantity: Order quantity as a float e.g. 0.001

    Returns:
        The validated quantity as a float

    Raises:
        ValueError: If quantity is zero or negative
    """
    if quantity <= 0:
        logger.warning(f"Validation failed: invalid quantity '{quantity}'")
        raise ValueError(
            f"Invalid quantity '{quantity}'. "
            f"Quantity must be greater than zero. Example: 0.001"
        )

    logger.debug(f"Quantity validated: {quantity}")
    return quantity


def validate_price(price: float, order_type: str) -> float:
    """
    Validates the order price.

    Rules:
      - Required for LIMIT orders (must be provided)
      - Must be greater than zero for LIMIT orders
      - Ignored for MARKET orders (Binance determines price)

    Args:
        price: Order price as a float e.g. 50000.0
        order_type: "MARKET" or "LIMIT" (already validated)

    Returns:
        The validated price as a float

    Raises:
        ValueError: If order is LIMIT and price is missing or invalid
    """
    if order_type == "LIMIT":
        # Price is required for LIMIT orders
        if price is None or price <= 0:
            logger.warning(f"Validation failed: invalid price '{price}' for LIMIT order")
            raise ValueError(
                f"Price is required for LIMIT orders and must be greater than zero. "
                f"Example: --price 50000.0"
            )
        logger.debug(f"Price validated for LIMIT order: {price}")

    else:
        # MARKET orders don't use price — log it and move on
        if price is not None and price > 0:
            logger.debug(f"Price '{price}' ignored for MARKET order")

    return price


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None
) -> dict:
    """
    Runs all validations in one call and returns clean values.

    This is the main function called by orders.py and cli.py.
    It validates every input and returns a clean dictionary
    ready to be passed to the Binance API.

    Args:
        symbol:     Trading pair e.g. "BTCUSDT"
        side:       "BUY" or "SELL"
        order_type: "MARKET" or "LIMIT"
        quantity:   Amount to trade e.g. 0.001
        price:      Price per unit (required for LIMIT) e.g. 50000.0

    Returns:
        Dictionary with all validated and normalized values:
        {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.001,
            "price": None
        }

    Raises:
        ValueError: If any input fails validation
    """
    logger.debug("Starting input validation...")

    # Run each validator — any failure raises ValueError immediately
    clean_symbol     = validate_symbol(symbol)
    clean_side       = validate_side(side)
    clean_order_type = validate_order_type(order_type)
    clean_quantity   = validate_quantity(quantity)
    clean_price      = validate_price(price, clean_order_type)

    logger.debug("All inputs validated successfully")

    # Return a clean dictionary of validated values
    return {
        "symbol":     clean_symbol,
        "side":       clean_side,
        "order_type": clean_order_type,
        "quantity":   clean_quantity,
        "price":      clean_price,
    }