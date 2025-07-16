import re
from datetime import datetime, timedelta
import os
import importlib.util

ROOT = os.path.dirname(os.path.dirname(__file__))
import sys
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location("telegram_pnl_bot", os.path.join(ROOT, "telegram_pnl_bot.py"))
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)
parse_dates = bot.parse_dates


def test_parse_no_args():
    start, end = parse_dates([])
    # Expect start to be roughly 30 days before end
    s = datetime.strptime(start, "%Y.%m.%d")
    e = datetime.strptime(end, "%Y.%m.%d")
    delta = e - s
    assert timedelta(days=29) <= delta <= timedelta(days=31)


def test_parse_explicit():
    start, end = parse_dates(["2024.01.01", "2024.02.01"])
    assert start == "2024.01.01"
    assert end == "2024.02.01"
