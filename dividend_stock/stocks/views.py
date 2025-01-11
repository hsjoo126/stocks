from django.shortcuts import render
import yfinance as yf
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr


def main(request):
    return render(request, "stocks/main.html")


def high(request):
    return render(request, "stocks/high.html")


def middle(request):
    # 나스닥(NASDAQ) 주식 정보 가져오기
    nasdaq_stocks = fdr.StockListing('NASDAQ')

    # Symbol 열만 추출
    symbols = nasdaq_stocks['Symbol']

    tickers = symbols[:100]

    stock_data = []
    for ticker_symbol in tickers:
        ticker = yf.Ticker(ticker_symbol)

        # 현재 주가
        current_price = ticker.info.get('currentPrice', '정보 없음')

        # 마지막 배당금
        dividends = ticker.dividends
        last_dividend_value = dividends.iloc[-1] if not dividends.empty else None

        # 마지막 배당일
        info = ticker.calendar
        dividend_date = None

        # info가 dict 형식인 경우, Dividend Date 항목을 확인
        if isinstance(info, dict) and 'Dividend Date' in info:
            dividend_date = info['Dividend Date']

        # info가 DataFrame 형식인 경우, Dividends 항목이 존재하는지 확인
        elif isinstance(info, pd.DataFrame) and 'Dividends' in info.index:
            dividend_date = info.loc['Dividends', 0]

        # 배당수익률
        yield_value = ticker.info.get('dividendYield', 0) * 100

        # 시가총액
        market_cap = ticker.info.get('marketCap', '정보 없음')

        if 4 <= yield_value <= 7:
            stock_data.append({
                'ticker': ticker_symbol,
                'current_price': current_price,
                'last_dividend': last_dividend_value,
                'dividend_date': dividend_date,
                'dividend_yield': round(yield_value, 2),
                'market_cap': "{:,}".format(market_cap) if isinstance(market_cap, int) else market_cap,
            })

    return render(request, "stocks/middle.html", {"stocks_data": stock_data})


def detail(request):
    return render(request, "stocks/detail.html")
