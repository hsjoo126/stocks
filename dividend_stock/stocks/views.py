from django.shortcuts import render
import yfinance as yf
import pandas as pd
import FinanceDataReader as fdr
from django.core.cache import cache 
from datetime import datetime, timedelta
from django.utils import timezone

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


def detail(request, ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    #시총
    market_cap = info.get('marketCap', '정보 없음')
    
    #주식 간단 정보
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
        dividend_list = dividend_data[['date', 'Dividends']].to_dict(orient='records')
    
    
    # 주가 내역 (최근 3개월)
    stock_history = stock.history(interval='1d', period='1y', auto_adjust=False)
    # 'Date' 열을 Datetime 형식으로 변환하고, 날짜만 출력
    stock_history['date'] = stock_history.index.date
    # 필요한 열만 선택
    stock_history_selected = stock_history[['date','Open', 'High', 'Low', 'Close', 'Volume']]
    # 데이터를 템플릿에 전달
    stock_history_list = stock_history_selected.to_dict(orient='records')


    context = {
        'stock':stock,
        'market_cap': market_cap,
        'summary': summary,
        'dividend_list': dividend_list,
        'stock_history_list': stock_history_list,
    }
    return render(request, "stocks/detail.html", context)
