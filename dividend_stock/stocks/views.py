from django.shortcuts import render
import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils import timezone
from stocks.models import Ticker,CollectedDividendData
import time
from django.core.paginator import Paginator


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

    paginator = Paginator(stock_data, 30) #stock_data를 30개씩 자르겠다는 의미
    page_number = request.GET.get('page')  # 유저가 선택한 'page'의 키값을 가져옴(템플릿 참고: ?page=)
    page_obj = paginator.get_page(page_number)  # 페이지 숫자에 맞는 데이터를 가져옴 (2페이지면 2페이지의 데이터)

    context = {
        "stocks_data" : page_obj.object_list, #page_obj.object_list: 현재 페이지 데이터만 포함.
        "page_obj" : page_obj, #page_obj: 페이지 데이터와 페이지네이션 정보를 모두 포함.
        "page_range": range(1, paginator.num_pages + 1),  #모든 페이지 번호, 1부터 마지막 페이지까지
    }


    # 템플릿에 데이터 전달
    return render(request, "stocks/high.html", context)

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

    paginator = Paginator(stock_data, 30) #stock_data를 30개씩 자르겠다는 의미
    page_number = request.GET.get('page')  # 유저가 선택한 'page'의 키값을 가져옴(템플릿 참고: ?page=)
    page_obj = paginator.get_page(page_number)  # 페이지 숫자에 맞는 데이터를 가져옴 (2페이지면 2페이지의 데이터)

    context = {
        "stocks_data" : page_obj.object_list, #page_obj.object_list: 현재 페이지 데이터만 포함.
        "page_obj" : page_obj, #page_obj: 페이지 데이터와 페이지네이션 정보를 모두 포함.
        "page_range": range(1, paginator.num_pages + 1),  #모든 페이지 번호, 1부터 마지막 페이지까지
    }

    # 템플릿에 데이터 전달
    return render(request, "stocks/middle.html", context)


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
