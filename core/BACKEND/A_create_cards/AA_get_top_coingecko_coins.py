import requests
import json

# === CONFIGURATION SECTION ===
API_URL = 'https://api.coingecko.com/api/v3/coins/markets'
VS_CURRENCY = 'usd'  # currency to compare against
ORDER = 'market_cap_desc'  # sorting order
PER_PAGE = 250  # items per API page
MAX_PAGES = 10  # max pages to fetch
LIMIT = 20  # total number of coins to collect
EXCLUDE_STABLECOINS = True  # exclude known stablecoins
OUTPUT_FILENAME = 'core/data/coins_db.json'  # output file name

# List of known stablecoins to exclude
STABLECOINS = {
    'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP', 'GUSD', 'USDN', 'SUSD', 'EURT',
    'EURS', 'XAUT', 'PAXG', 'FEI', 'FRAX', 'UST', 'LUSD', 'HUSD', 'ALUSD', 'USDD',
    'USD', 'USDS', 'USDX', 'CUSD', 'MIM', 'MUSD', 'USDJ', 'USDK', 'USDQ'
}
# === END CONFIGURATION SECTION ===

def fetch_top_coins():
    """Fetch top coins from CoinGecko API, excluding stablecoins if configured"""
    params = {
        'vs_currency': VS_CURRENCY,
        'order': ORDER,
        'per_page': PER_PAGE,
        'page': 1,
        'sparkline': 'false'
    }

    coins = []
    while len(coins) < LIMIT and params['page'] <= MAX_PAGES:
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            print(f"Error during request: {response.status_code}")
            break
        data = response.json()
        for coin in data:
            symbol_upper = coin['symbol'].upper()
            if EXCLUDE_STABLECOINS and symbol_upper in STABLECOINS:
                continue
            coins.append({
                'id': coin['id'],
                'symbol': coin['symbol'],
                'name': coin['name'],
                'market_cap': coin['market_cap'],
                'current_price': coin['current_price']
            })
            if len(coins) >= LIMIT:
                break
        params['page'] += 1
    return coins

def save_to_json(data):
    """Save the data to a JSON file"""
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    """Main execution function"""
    top_coins = fetch_top_coins()
    save_to_json(top_coins)

if __name__ == '__main__':
    main()
