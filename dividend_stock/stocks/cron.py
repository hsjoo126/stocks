import yfinance as yf
import FinanceDataReader as fdr
from django.core.cache import cache
import pandas as pd
from stocks.models import Ticker, DividendTicker, CollectedDividendData
import time
from time import sleep



#update_dividend_data 실행시 last_dividend가 NULL로 나오는 문제가 생겨서
# last_dividend만 따로 수집
def update_last_dividend():
    # CollectedDividendData에서 모든 주식 가져오기
    stocks = CollectedDividendData.objects.all()

    # 주식별로 처리
    for stock in stocks:
        ticker_symbol = stock.ticker  # CollectedDividendData의 ticker 필드 사용
        try:
            # Yahoo Finance에서 데이터 가져오기
            ticker_data = yf.Ticker(ticker_symbol)
            dividends = ticker_data.dividends

            # 마지막 배당금 확인
            last_dividend = dividends.iloc[-1] if not dividends.empty else None

            # CollectedDividendData의 last_dividend 필드 업데이트
            if last_dividend is not None:
                stock.last_dividend = last_dividend
                stock.save()  # 변경 내용 저장
                print(f"Updated last_dividend for {ticker_symbol}: {last_dividend}")
            else:
                print(f"No dividends found for {ticker_symbol}. Skipping.")
        except Exception as e:
            print(f"Error updating last_dividend for {ticker_symbol}: {e}")

    print("마지막 배당금 항목의 업데이트 완료했습니다.")



# 배당관련 데이터 있는 주식을 가지고 원하는 데이터 수집
def update_dividend_data():
    
    tickers = DividendTicker.objects.all()  # DividendTicker에서 티커 가져오기
    batch_size = 100  # 한 번에 처리할 티커 개수

    # 티커 배치별 처리
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]  # 100개씩 배치 처리

        # 배치 내 티커 처리
        for ticker_obj in batch:
            ticker_symbol = ticker_obj.symbol
            try:
                ticker_data = yf.Ticker(ticker_symbol)

                # 종가 가져오기 (최근 1일 기준)
                data = ticker_data.history(period="1d")
                close = data['Close'].iloc[-1] if not data.empty else None  # 종가가 없으면 None

                # 배당금 정보
                dividends = ticker_data.dividends
                last_dividend = dividends.iloc[-1] if not dividends.empty else None

                # 배당일 처리 (calendar에서 'Dividend Date'를 추출)
                calendar = ticker_data.calendar
                dividend_date = None
                try:
                    # calendar가 dict인 경우에 'Dividend Date' 키 확인
                    if isinstance(calendar, dict) and 'Dividend Date' in calendar:
                        dividend_date = calendar['Dividend Date']
                    else:
                        print(f"No 'Dividend Date' for {ticker_symbol}, likely no dividends.")
                        dividend_date = "정보없음"
                except Exception as e:
                    print(f"Error parsing Dividend Date for {ticker_symbol}: {e}, Type of calendar: {type(calendar)}")
                # 배당률과 시가총액
                dividend_yield = ticker_data.info.get('dividendYield', '정보없음')
                if isinstance(dividend_yield, (int, float)):  # 숫자인 경우에만 처리
                    dividend_yield = dividend_yield * 100
                market_cap = ticker_data.info.get('marketCap','정보 없음')
                if isinstance(market_cap, (int, float)):
                    market_cap = "{:,}".format(market_cap)  # 숫자일 때 쉼표 추가
                else:
                    market_cap = market_cap  # '정보 없음' 그대로 사용

                # 저장할 데이터 생성
                dividend_yield_category = None
                if isinstance(dividend_yield, (int, float)):
                    if 4 <= dividend_yield <= 7:
                        dividend_yield_category = "4_to_7"
                    elif dividend_yield > 7:
                        dividend_yield_category = "above_7"

                # CollectedDividendData에 데이터 저장
                if dividend_yield_category:
                    CollectedDividendData.objects.update_or_create(
                        ticker=ticker_symbol,
                        defaults={
                            "close": close,  # 종가 사용
                            "last_dividend": last_dividend,
                            "dividend_date": dividend_date,
                            "dividend_yield": round(dividend_yield, 2),
                            "market_cap": market_cap,
                            "dividend_yield_category": dividend_yield_category,
                        },
                    )
            except Exception as e:
                print(f"Error fetching data for {ticker_symbol}: {e}")

        # 각 배치마다 10초 대기 후, 처리된 티커 수 출력
        print(f"Processed {i + batch_size} tickers. Waiting for 10 seconds...")
        time.sleep(10)
    
    print("배당 주식의 데이터 수집이 완료되었습니다.")


#Ticker에 있는 것 중에서 배당관련 데이터가 있는 애들만 수집
def check_and_filter_dividends():
    tickers = Ticker.objects.all()
    dividend_tickers = []

    # 100개씩 분할하여 처리(429 오류 방지)
    batch_size = 100
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]

        for ticker in batch:
            try:
                stock = yf.Ticker(ticker.symbol)

                # dividends 확인
                dividends = stock.dividends

                if not dividends.empty:  
                    dividend_tickers.append(DividendTicker(
                        symbol=ticker.symbol,
                        market=ticker.market
                    ))
            except Exception as e:
                print(f"Error processing {ticker.symbol}: {e}")

        DividendTicker.objects.bulk_create(dividend_tickers, ignore_conflicts=True)
        dividend_tickers = []  # 다음 배치를 위해 리스트 초기화

        # 10초 대기
        print(f"Processed {i + batch_size} tickers. Waiting for 10 seconds...")
        sleep(10)
    print("배당 관련 ticker만 걸러내는 작업을 완료했습니다.")


#나스닥과 뉴욕증권 거래소에 있는 ticker 수집
def update_tickers():
    nasdaq_stocks = fdr.StockListing('NASDAQ')
    nyse_stocks = fdr.StockListing('NYSE')

    # NASDAQ 티커 저장
    for _, row in nasdaq_stocks.iterrows():
        symbol = row['Symbol']
        Ticker.objects.get_or_create(symbol=symbol, defaults={'market': 'NASDAQ'})

    # NYSE 티커 저장
    for _, row in nyse_stocks.iterrows():
        symbol = row['Symbol']
        Ticker.objects.get_or_create(symbol=symbol, defaults={'market': 'NYSE'})

    print("나스닥과 뉴욕 증권 거래소의 모든 ticker 수집을 완료했습니다.")