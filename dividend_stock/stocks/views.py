from django.shortcuts import render
import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils import timezone
from stocks.models import Ticker,CollectedDividendData
import time


def main(request):
    return render(request, "stocks/main.html")


def high(request):
    # Redis에서 데이터 가져오기
    cache_key = "stock_data_above_7"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우 DB에서 데이터 조회
    if not stock_data:
        # DB에서 배당률 7% 이상인 데이터 조회 (dividend_yield_category 필드 기준)
        stock_data = []
        stocks = CollectedDividendData.objects.filter(dividend_yield_category='above_7')

        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'close': stock.close,
                'last_dividend': stock.last_dividend,
                'dividend_date': stock.dividend_date,
                'dividend_yield': stock.dividend_yield,
                'market_cap': stock.market_cap,
            })

        # DB에서 조회한 데이터를 Redis에 캐시
        cache.set(cache_key, stock_data)

    # 템플릿에 데이터 전달
    return render(request, "stocks/high.html", {"stocks_data": stock_data})

def middle(request):
    # Redis에서 데이터 가져오기
    cache_key = "stock_data_4_to_7"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우 DB에서 데이터 조회
    if not stock_data:
        # DB에서 배당률 7% 이상인 데이터 조회 (dividend_yield_category 필드 기준)
        stock_data = []
        stocks = CollectedDividendData.objects.filter(dividend_yield_category='4_to_7')

        for stock in stocks:
            stock_data.append({
                'ticker': stock.ticker,
                'close': stock.close,
                'last_dividend': stock.last_dividend,
                'dividend_date': stock.dividend_date,
                'dividend_yield': stock.dividend_yield,
                'market_cap': stock.market_cap,
            })

        # DB에서 조회한 데이터를 Redis에 캐시
        cache.set(cache_key, stock_data)

    # 템플릿에 데이터 전달
    return render(request, "stocks/middle.html", {"stocks_data": stock_data})


def detail(request, ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    # 시총
    market_cap = info.get('marketCap', '정보 없음')
    if isinstance(market_cap, (int, float)):
        market_cap = "{:,}".format(market_cap)  # 숫자일 때 쉼표 추가
    else:
        market_cap = market_cap  # '정보 없음' 그대로 사용


    # 주식 간단 정보
    summary = info.get('longBusinessSummary', '정보 없음')

    # 배당 내역
    divi = stock.dividends
    # 배당 내역이 비어있는지 확인
    if divi.empty:
        dividend_data = "배당 내역이 없습니다."  # 배당 내역이 없으면 메시지 반환
    else:
        # 최근 3년 기준 날짜 계산
        three_years_ago = timezone.now() - timedelta(days=3*365)

        # 최근 3년 데이터 필터링 후 인덱스를 리셋하고 'Date' 컬럼을 날짜로 변환
        dividend_data = divi[divi.index >= three_years_ago].reset_index()
        dividend_data['date'] = dividend_data['Date'].dt.date  # 날짜만 추출

        # 배당금과 날짜만 선택하여 리스트로 변환
        dividend_list = dividend_data[[
            'date', 'Dividends']].to_dict(orient='records')

    # 주가 내역 (최근 3개월)
    stock_history = stock.history(
        interval='1d', period='1y', auto_adjust=False)
    # 'Date' 열을 Datetime 형식으로 변환하고, 날짜만 출력
    stock_history['date'] = stock_history.index.date
    # 필요한 열만 선택
    stock_history_selected = stock_history[[
        'date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    # 데이터를 템플릿에 전달
    stock_history_list = stock_history_selected.to_dict(orient='records')

    context = {
        'stock': stock,
        'market_cap': market_cap,
        'summary': summary,
        'dividend_list': dividend_list,
        'stock_history_list': stock_history_list,
    }
    return render(request, "stocks/detail.html", context)
