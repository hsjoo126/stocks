import yfinance as yf
import FinanceDataReader as fdr
from django.core.cache import cache
import pandas as pd


def update_stock_data():
    # Redis 캐시 키 설정
    keys = {
        "4_to_7_percent": "stock_data_4_to_7",
        "above_7_percent": "stock_data_above_7",
    }

    # 1. 나스닥 상위 종목가져오기
    nasdaq_stocks = fdr.StockListing('NASDAQ')
    tickers = nasdaq_stocks['Symbol'][:100]  # 상위 30개 종목만 선택

    stock_data_4_to_7 = []
    stock_data_above_7 = []

    # 2. 각 티커에 대해 데이터 수집
    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)

            # 데이터 수집
            current_price = ticker.info.get('currentPrice', '정보없음')
            dividends = ticker.dividends
            last_dividend_value = dividends.iloc[-1] if not dividends.empty else None

            # 마지막 배당일
            info = ticker.calendar
            dividend_date = None

            # info가 dict 형식인 경우
            if isinstance(info, dict) and 'Dividend Date' in info:
                dividend_date = info['Dividend Date']

            # info가 DataFrame 형식인 경우
            elif isinstance(info, pd.DataFrame) and 'Dividends' in info.index:
                dividend_date = info.loc['Dividends', 0]

            yield_value = ticker.info.get('dividendYield', 0) * 100
            market_cap = ticker.info.get('marketCap')

            # 4~7% 배당률 데이터
            if 4 <= yield_value <= 7:
                stock_data_4_to_7.append({
                    'ticker': ticker_symbol,
                    'current_price': current_price,
                    'last_dividend': last_dividend_value,
                    'dividend_date': dividend_date,
                    'dividend_yield': round(yield_value, 2),
                    'market_cap': "{:,}".format(market_cap) if market_cap else None,
                })

            # 7% 초과 배당률 데이터
            if yield_value > 7:
                stock_data_above_7.append({
                    'ticker': ticker_symbol,
                    'current_price': current_price,
                    'last_dividend': last_dividend_value,
                    'dividend_date': dividend_date,
                    'dividend_yield': round(yield_value, 2),
                    'market_cap': "{:,}".format(market_cap) if market_cap else None,
                })

        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")

    # 3. Redis에 데이터 저장 (30분 TTL)
    cache.set(keys["4_to_7_percent"], stock_data_4_to_7)
    cache.set(keys["above_7_percent"], stock_data_above_7)

    print("각 페이지별 주식 데이터가 업데이트 되었습니다!")
