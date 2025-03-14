import yfinance as yf
import FinanceDataReader as fdr
from stocks.models import Ticker, CollectedDividendData
import time


def update_dividend_data():
    
    tickers = Ticker.objects.all() 
    batch_size = 100
    
    # 티커 배치별 처리
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        # 배치 내 티커 처리
        for ticker_obj in batch:
            ticker_symbol = ticker_obj.symbol
            try:
                ticker_data = yf.Ticker(ticker_symbol)
                dividends = ticker_data.dividends
                if dividends.empty:
                    continue
                dividend_yield = ticker_data.info.get('dividendYield')
                if isinstance(dividend_yield, (int, float)):
                    if 4 <= dividend_yield <= 7:
                        dividend_yield_category = "4_to_7"
                    elif dividend_yield > 7:
                        dividend_yield_category = "above_7"
                    else:
                        continue
                else:
                    continue

                # 종가 (최근 1일 기준)
                data = ticker_data.history(period="1d")
                close = data['Close'].iloc[-1] if not data.empty else None

                # 배당금 정보
                last_dividend = dividends.iloc[-1] if not dividends.empty else None

                # 배당일 처리 (calendar에서 'Dividend Date'를 추출)
                calendar = ticker_data.calendar
                dividend_date = None
                try:
                    # calendar가 dict인 경우에 'Dividend Date' 키 확인
                    if isinstance(calendar, dict) and 'Dividend Date' in calendar:
                        dividend_date = calendar['Dividend Date']
                    else:
                        dividend_date = "정보없음"
                except Exception as e:
                    print(f"Error parsing Dividend Date for {ticker_symbol}: {e}, Type of calendar: {type(calendar)}")
                # 시가총액
                market_cap = ticker_data.info.get('marketCap','정보 없음')
                if isinstance(market_cap, (int, float)):
                    market_cap = "{:,}".format(market_cap)  # 숫자일 때 쉼표 추가

                # CollectedDividendData에 데이터 저장
                CollectedDividendData.objects.update_or_create(
                    ticker=ticker_symbol,
                    defaults={
                        "close": close,
                        "last_dividend": last_dividend,
                        "dividend_date": dividend_date,
                        "dividend_yield": dividend_yield,
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