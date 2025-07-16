import os
import json
from datetime import date

from Ozon4.fetchers.Products import Products


def build_headers() -> dict:
    client_id = os.environ.get("OZON_CLIENT_ID")
    api_key = os.environ.get("OZON_API_KEY")
    if not client_id or not api_key:
        raise RuntimeError("OZON_CLIENT_ID and OZON_API_KEY must be set")
    return {"Client-Id": client_id, "Api-Key": api_key}


if __name__ == "__main__":
    headers = build_headers()
    products = Products(headers)
    products.run()
    product_count = len(products.products)
    result = {"date": date.today().isoformat(), "product_count": product_count}
    with open("product_count.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
