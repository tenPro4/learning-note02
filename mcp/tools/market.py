from polygon import StocksClient, ReferenceClient
from dotenv import load_dotenv
import os
from datetime import datetime
import random
from tools.database import write_market, read_market
from functools import lru_cache
from datetime import timezone

load_dotenv(override=True)

# polygon_api_key = os.getenv("POLYGON_API_KEY")
# polygon_plan = os.getenv("POLYGON_PLAN")

polygon_api_key = "UxKLpE_Yt5zCv3_B86Ver1E0cNAKyELj"
polygon_plan = "free"

is_paid_polygon = polygon_plan == "paid"
is_realtime_polygon = polygon_plan == "realtime"


def is_market_open() -> bool:
    client = ReferenceClient(polygon_api_key)
    market_status = client.get_market_status()
    return market_status.get('market') == "open"


def get_all_share_prices_polygon_eod() -> dict[str, float]:
    client = StocksClient(polygon_api_key)

    # 1. get_previous_close returns {'results': [{...}]}
    resp = client.get_previous_close("SPY")
    if not resp or 'results' not in resp:
        raise ValueError("No data returned from Polygon")
        
    probe = resp['results'][0]
    # 2. Use ['t'] for timestamp (Unix milliseconds)
    last_close = datetime.fromtimestamp(probe['t'] / 1000, tz=timezone.utc).date()

    # 3. get_grouped_daily_bars returns {'results': [{'T': 'AAPL', 'c': 150.0}, ...]}
    data = client.get_grouped_daily_bars(last_close, adjusted=True)
    results = data.get('results', [])
    
    # 4. Use ['T'] for Ticker and ['c'] for Close price
    return {result['T']: result['c'] for result in results}


@lru_cache(maxsize=2)
def get_market_for_prior_date(today):
    market_data = read_market(today)
    if not market_data:
        market_data = get_all_share_prices_polygon_eod()
        write_market(today, market_data)
    return market_data


def get_share_price_polygon_eod(symbol) -> float:
    today = datetime.now().date().strftime("%Y-%m-%d")
    market_data = get_market_for_prior_date(today)
    return market_data.get(symbol, 0.0)


def get_share_price_polygon_min(symbol) -> float:
    client = StocksClient(polygon_api_key)
    result = client.get_snapshot(symbol)
    
    # Snapshot dict is deeply nested: ticker -> lastTrade -> p
    ticker_data = result.get('ticker', {})
    price = ticker_data.get('lastTrade', {}).get('p') or \
            ticker_data.get('prevDay', {}).get('c')
            
    return float(price) if price else 0.0


def get_share_price_polygon(symbol) -> float:
    if is_paid_polygon:
        return get_share_price_polygon_min(symbol)
    else:
        return get_share_price_polygon_eod(symbol)


def get_share_price(symbol) -> float:
    if polygon_api_key:
        try:
            return get_share_price_polygon(symbol)
        except Exception as e:
            print(f"Was not able to use the polygon API due to {e}; using a random number")
    return float(random.randint(1, 100))
