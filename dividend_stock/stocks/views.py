from django.shortcuts import render
import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
from django.core.cache import cache 

def main(request):
    return render(request, "stocks/main.html")


def high(request):
    # Redis에서 데이터 가져오기
    cache_key = "stock_data_above_7"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우, 실시간으로 데이터 수집
    if not stock_data:
        nasdaq_stocks = fdr.StockListing('NASDAQ')
        tickers = nasdaq_stocks['Symbol'][:100]  
        stock_data = []

        for ticker_symbol in tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)

                # 데이터 수집
                current_price = ticker.info.get('currentPrice','정보없음')
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

                # 7%초과 배당률 필터링
                if yield_value > 7:
                    stock_data.append({
                        'ticker': ticker_symbol,
                        'current_price': current_price,
                        'last_dividend': last_dividend_value,
                        'dividend_date': dividend_date,
                        'dividend_yield': round(yield_value, 2),
                        'market_cap': "{:,}".format(market_cap) if market_cap else None,
                    })
            except Exception as e:
                print(f"Error fetching data for {ticker_symbol}: {e}")

        cache.set(cache_key, stock_data)

    # 템플릿에 데이터 전달
    return render(request, "stocks/high.html", {"stocks_data": stock_data})



def middle(request):
    # Redis에서 데이터 가져오기
    cache_key = "stock_data_4_to_7"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우, 실시간으로 데이터 수집
    if not stock_data:
        nasdaq_stocks = fdr.StockListing('NASDAQ')
        tickers = nasdaq_stocks['Symbol'][:100]  
        stock_data = []

        for ticker_symbol in tickers:
            try:
                ticker = yf.Ticker(ticker_symbol)

                # 데이터 수집
                current_price = ticker.info.get('currentPrice','정보없음')
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

                # 4~7% 배당률 필터링
                if 4 <= yield_value <= 7:
                    stock_data.append({
                        'ticker': ticker_symbol,
                        'current_price': current_price,
                        'last_dividend': last_dividend_value,
                        'dividend_date': dividend_date,
                        'dividend_yield': round(yield_value, 2),
                        'market_cap': "{:,}".format(market_cap) if market_cap else None,
                    })
            except Exception as e:
                print(f"Error fetching data for {ticker_symbol}: {e}")

        cache.set(cache_key, stock_data)

    # 템플릿에 데이터 전달
    return render(request, "stocks/middle.html", {"stocks_data": stock_data})


def detail(request):
    return render(request, "stocks/detail.html")
