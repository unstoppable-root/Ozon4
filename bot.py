import os
import logging
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from fetchers.Finance import AsyncFinanceRealizationList

load_dotenv()

CLIENT_ID = os.getenv("OZON_CLIENT_ID")
API_KEY = os.getenv("OZON_API_KEY")

def calculate_pnl(operations):
    """Simple PnL calculation from list of operations."""
    total = 0.0
    for op in operations:
        amount = op.get("amount") or op.get("operation_sum") or 0
        try:
            total += float(amount)
        except (TypeError, ValueError):
            continue
    return total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправьте /pnl YYYY.MM.DD YYYY.MM.DD для получения отчета"
    )


async def pnl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /pnl YYYY.MM.DD YYYY.MM.DD"
        )
        return
    start, end = context.args[0], context.args[1]
    headers = {
        "Client-Id": os.getenv("OZON_CLIENT_ID", ""),
        "Api-Key": os.getenv("OZON_API_KEY", ""),
    }
    fetcher = AsyncFinanceRealizationList(headers, start, end)
    await fetcher.run_in_jupyter()
    pnl_value = calculate_pnl(fetcher.data)
    await update.message.reply_text(
        f"PnL за период {start} - {end}: {pnl_value:.2f}"
    )


def main() -> None:
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pnl", pnl))
    app.run_polling()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="api_requests_error.log",
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
    )
    main()
