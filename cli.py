# cli.py
# -------------------------------------------------------
# CLI Entry Point for the Trading Bot
# -------------------------------------------------------
# This is the main file users run from the terminal.
# It wires together all layers of the application:
#   logging → validation → order placement → output
#
# Usage examples:
#   MARKET BUY:
#     python cli.py place-order --symbol BTCUSDT --side BUY
#                               --order-type MARKET --quantity 0.001
#
#   LIMIT SELL:
#     python cli.py place-order --symbol BTCUSDT --side SELL
#                               --order-type LIMIT --quantity 0.001
#                               --price 50000.0
# -------------------------------------------------------

import typer
from typing import Optional
from binance.exceptions import BinanceAPIException, BinanceOrderException

from bot.logging_config import setup_logging, get_logger
from bot.client import get_client
from bot.validators import validate_all
from bot.orders import place_order

# -------------------------------------------------------
# Initialize Typer app
# -------------------------------------------------------
# This creates the CLI application instance
# rich_markup_mode="rich" enables colored terminal output
app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot — Place MARKET and LIMIT orders.",
    rich_markup_mode="rich"
)

# Logger for this module
# setup_logging() is called inside the command before this is used
logger = get_logger(__name__)


@app.command()
def place_order_cmd(
    symbol: str = typer.Option(
        ...,                        # "..." means required — no default
        "--symbol",
        help="Trading pair symbol. Example: BTCUSDT",
    ),
    side: str = typer.Option(
        ...,
        "--side",
        help="Order side: BUY or SELL",
    ),
    order_type: str = typer.Option(
        ...,
        "--order-type",
        help="Order type: MARKET or LIMIT",
    ),
    quantity: float = typer.Option(
        ...,
        "--quantity",
        help="Order quantity. Example: 0.001",
    ),
    price: Optional[float] = typer.Option(
        None,                       # Optional — only required for LIMIT
        "--price",
        help="Order price (required for LIMIT orders). Example: 50000.0",
    ),
):
    """
    Place a MARKET or LIMIT order on Binance Futures Testnet.

    Examples:\n
      [bold]MARKET BUY:[/bold]\n
        python cli.py place-order --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001\n
      [bold]LIMIT SELL:[/bold]\n
        python cli.py place-order --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 50000.0
    """

    # -------------------------------------------------------
    # Step 1: Initialize logging
    # -------------------------------------------------------
    # This must be called first so all subsequent logs work
    setup_logging()
    logger.info("=" * 60)
    logger.info("Trading Bot started")

    # -------------------------------------------------------
    # Step 2: Print order request summary
    # -------------------------------------------------------
    # Show the user what they're about to place
    # before we validate or send anything
    typer.echo("")
    typer.echo("=" * 50)
    typer.echo("        BINANCE FUTURES TESTNET BOT")
    typer.echo("=" * 50)
    typer.echo("  ORDER REQUEST SUMMARY")
    typer.echo("-" * 50)
    typer.echo(f"  Symbol     : {symbol.upper()}")
    typer.echo(f"  Side       : {side.upper()}")
    typer.echo(f"  Order Type : {order_type.upper()}")
    typer.echo(f"  Quantity   : {quantity}")
    typer.echo(f"  Price      : {price if price else 'N/A (MARKET)'}")
    typer.echo("-" * 50)

    logger.info(
        f"Order request | symbol={symbol} side={side} "
        f"type={order_type} qty={quantity} price={price}"
    )

    # -------------------------------------------------------
    # Step 3: Validate all inputs
    # -------------------------------------------------------
    try:
        validated = validate_all(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        logger.info("Input validation passed")

    except ValueError as e:
        # Validation failed — show clear error and exit
        logger.error(f"Validation error: {e}")
        typer.echo(f"\n  [ERROR] Invalid input: {e}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)

    # -------------------------------------------------------
    # Step 4: Connect to Binance Futures Testnet
    # -------------------------------------------------------
    typer.echo("  Connecting to Binance Futures Testnet...")

    try:
        client = get_client()
        typer.echo("  Connection successful!")
        logger.info("Binance client initialized successfully")

    except ValueError as e:
        # Missing API keys
        logger.error(f"Client setup error: {e}")
        typer.echo(f"\n  [ERROR] Configuration error: {e}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)

    except ConnectionError as e:
        # Network/connection failure
        logger.error(f"Connection error: {e}")
        typer.echo(f"\n  [ERROR] Connection failed: {e}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)

    # -------------------------------------------------------
    # Step 5: Place the order
    # -------------------------------------------------------
    typer.echo(f"  Placing {validated['order_type']} order...")

    try:
        result = place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"]
        )

        # -------------------------------------------------------
        # Step 6: Print order response details
        # -------------------------------------------------------
        typer.echo("")
        typer.echo("=" * 50)
        typer.echo("  ORDER RESPONSE")
        typer.echo("-" * 50)
        typer.echo(f"  Order ID     : {result['order_id']}")
        typer.echo(f"  Symbol       : {result['symbol']}")
        typer.echo(f"  Side         : {result['side']}")
        typer.echo(f"  Type         : {result['type']}")
        typer.echo(f"  Quantity     : {result['quantity']}")
        typer.echo(f"  Status       : {result['status']}")
        typer.echo(f"  Executed Qty : {result['executed_qty']}")
        typer.echo(f"  Avg Price    : {result['avg_price']}")
        typer.echo("-" * 50)
        typer.echo("  SUCCESS: Order placed successfully!")
        typer.echo("=" * 50)
        typer.echo("")

        logger.info(
            f"Order completed successfully | "
            f"OrderId={result['order_id']} | "
            f"Status={result['status']}"
        )

    except BinanceAPIException as e:
        # Binance rejected the order
        logger.error(f"Binance API error: [{e.status_code}] {e.message}")
        typer.echo("")
        typer.echo("-" * 50)
        typer.echo(f"  [FAILED] Binance API Error")
        typer.echo(f"  Code    : {e.status_code}")
        typer.echo(f"  Message : {e.message}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)

    except BinanceOrderException as e:
        # Order-specific error
        logger.error(f"Binance order error: [{e.status_code}] {e.message}")
        typer.echo("")
        typer.echo("-" * 50)
        typer.echo(f"  [FAILED] Order Error")
        typer.echo(f"  Code    : {e.status_code}")
        typer.echo(f"  Message : {e.message}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)

    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error: {e}")
        typer.echo("")
        typer.echo("-" * 50)
        typer.echo(f"  [FAILED] Unexpected error: {e}")
        typer.echo("=" * 50)
        raise typer.Exit(code=1)


# -------------------------------------------------------
# Entry point
# -------------------------------------------------------
# This allows running the bot as:
#   python cli.py place-order ...
if __name__ == "__main__":
    app()