import os
from datetime import datetime, timedelta
from typing import List, Dict

from pandas import DataFrame
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


def _build_headers() -> Dict[str, str]:
    client_id = os.environ.get("OZON_CLIENT_ID")
    api_key = os.environ.get("OZON_API_KEY")
    if not client_id or not api_key:
        raise RuntimeError("OZON_CLIENT_ID and OZON_API_KEY must be set")
    return {"Client-Id": client_id, "Api-Key": api_key}


def parse_dates(args: List[str]) -> (str, str):
    """Parse command arguments and return start and end dates.

    If no arguments are provided, the last 30 days are used. When two
    arguments are passed they must be in ``YYYY.MM.DD`` format.
    """
    if not args:
        end_dt = datetime.today()
        start_dt = end_dt - timedelta(days=30)
        return start_dt.strftime("%Y.%m.%d"), end_dt.strftime("%Y.%m.%d")

    if len(args) != 2:
        raise ValueError("Please provide start and end dates in YYYY.MM.DD format")

    start, end = args
    datetime.strptime(start, "%Y.%m.%d")
    datetime.strptime(end, "%Y.%m.%d")
    return start, end


async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        start, end = parse_dates(context.args)
        from fetchers.Finance import AsyncFinanceRealizationList

        finance = AsyncFinanceRealizationList(_build_headers(), start, end)
        await finance.run_in_jupyter()
        df = DataFrame(finance.data)
        if df.empty:
            await update.message.reply_text("No data for the specified period")
            return
        csv_data = df.to_csv(index=False)
        await update.message.reply_document(document=InputFile.from_bytes(csv_data.encode(), filename="pnl.csv"))
    except Exception as exc:
        await update.message.reply_text(f"Error: {exc}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send usage instructions."""
    msg = (
        "Use /pnl <start YYYY.MM.DD> <end YYYY.MM.DD> to receive a report.\n"
        "If dates are omitted the last 30 days are used."
    )
    await update.message.reply_text(msg)


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN not set")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("pnl", pnl_command))

    app.run_polling()


if __name__ == "__main__":
    main()
