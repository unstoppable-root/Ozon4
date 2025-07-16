import os
import asyncio
from datetime import datetime
from typing import List, Dict

from pandas import DataFrame
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from fetchers.Finance import AsyncFinanceRealizationList


def _build_headers() -> Dict[str, str]:
    client_id = os.environ.get("OZON_CLIENT_ID")
    api_key = os.environ.get("OZON_API_KEY")
    if not client_id or not api_key:
        raise RuntimeError("OZON_CLIENT_ID and OZON_API_KEY must be set")
    return {"Client-Id": client_id, "Api-Key": api_key}


def parse_dates(args: List[str]) -> (str, str):
    if len(args) != 2:
        raise ValueError("Please provide start and end dates in YYYY.MM.DD format")
    start, end = args
    # Validate format
    datetime.strptime(start, "%Y.%m.%d")
    datetime.strptime(end, "%Y.%m.%d")
    return start, end


async def pnl_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        start, end = parse_dates(context.args)
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


def main() -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN not set")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("pnl", pnl_command))

    app.run_polling()


if __name__ == "__main__":
    main()
