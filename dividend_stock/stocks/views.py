from django.shortcuts import render
import yfinance as yf
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
from stocks.models import CollectedDividendData
from django.core.paginator import Paginator
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def main(request):
    return render(request, "stocks/main.html")


def high(request):
    sort_order = request.GET.get("sort", "asc")
    sort_field = request.GET.get("field", "ticker")

    if sort_order == "asc":
        order_by_field = sort_field
    else:
        order_by_field = f"-{sort_field}"

    # Redis에서 데이터 가져오기
    cache_key = f"stock_data_above_7_{sort_order}_{sort_field}"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우 DB에서 데이터 조회
    if not stock_data:
        # DB에서 배당률 7% 이상인 데이터 조회 (dividend_yield_category 필드 기준)
        stock_data = []
        stocks = CollectedDividendData.objects.filter(dividend_yield_category='above_7').order_by(order_by_field)

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

    paginator = Paginator(stock_data, 30) 
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    context = {
        "stocks_data" : page_obj.object_list,
        "page_obj" : page_obj,
        "page_range": range(1, paginator.num_pages + 1), 
        "sort_order": sort_order,
        "sort_field": sort_field,
    }


    # 템플릿에 데이터 전달
    return render(request, "stocks/high.html", context)

def middle(request):
    sort_order = request.GET.get("sort", "asc")
    sort_field = request.GET.get("field", "ticker")

    if sort_order == "asc":
        order_by_field = sort_field
    else:
        order_by_field = f"-{sort_field}"
    # Redis에서 데이터 가져오기
    cache_key = f"stock_data_4_to_7_{sort_order}_{sort_field}"
    stock_data = cache.get(cache_key)

    # Redis에 데이터가 없을 경우 DB에서 데이터 조회
    if not stock_data:
        stock_data = []
        stocks = CollectedDividendData.objects.filter(dividend_yield_category='4_to_7').order_by(order_by_field)

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

    paginator = Paginator(stock_data, 30)
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)
    context = {
        "stocks_data" : page_obj.object_list, 
        "page_obj" : page_obj,
        "page_range": range(1, paginator.num_pages + 1),
        "sort_order": sort_order,
        "sort_field": sort_field,
    }

    # 템플릿에 데이터 전달
    return render(request, "stocks/middle.html", context)


def detail(request, ticker):
    stock = yf.Ticker(ticker)

    # 시총
    market_cap = stock.info.get('marketCap', '정보 없음')
    if isinstance(market_cap, (int, float)):
        market_cap = "{:,}".format(market_cap)
    else:
        market_cap = market_cap

    # 현재 주가
    current_price = stock.info.get('currentPrice', '정보 없음')
    # 배당일 처리 (calendar에서 'Dividend Date'를 추출)
    calendar = stock.calendar
    dividend_date = None
    try:
        # calendar가 dict인 경우에 'Dividend Date' 키 확인
        if isinstance(calendar, dict) and 'Dividend Date' in calendar:
            dividend_date = calendar['Dividend Date']
        else:
            print(f"No 'Dividend Date' for {stock}, likely no dividends.")
            dividend_date = "정보없음"
    except Exception as e:
        print(f"Error parsing Dividend Date for {stock}: {e}, Type of calendar: {type(calendar)}")
    # 배당금 정보
    dividends = stock.dividends
    last_dividend = dividends.iloc[-1] if not dividends.empty else None
    #배당수익률
    dividend_yield = stock.info.get('dividendYield', '정보 없음')


    # 주식 간단 정보
    summary = stock.info.get('longBusinessSummary', '정보 없음')

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

    # 주가 내역
    stock_history = stock.history(
        interval='1d', period='1y', auto_adjust=False)
    # 'Date' 열을 Datetime 형식으로 변환하고, 날짜만 출력
    stock_history['date'] = stock_history.index.date
    # 필요한 열만 선택
    stock_history_selected = stock_history[[
        'date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    # 데이터를 템플릿에 전달
    stock_history_list = stock_history_selected.to_dict(orient='records')

    #주가그래프
    matplotlib.use('Agg') #non-GUI 백엔드 Agg 사용
    #폰트 설정
    matplotlib.rc('font', family='NanumGothic')
    close_prices = stock_history[['date', 'Close']]  # 날짜와 종가만 선택
    #그래프 그리기
    plt.figure(figsize=(8, 4))
    plt.plot(close_prices['date'], close_prices['Close'], label='주가', color='#7cfae8',  linewidth=2)
    plt.title(f'1년간 {ticker} 주식 그래프 (종가 기준)',color='white')
    plt.xticks(close_prices['date'][::30], rotation=45,color='white')  # x축 레이블 간격 조정 및 회전
    plt.ylabel('주가 (USD)',color='white')
    plt.yticks(color="white")
    plt.legend(facecolor='#4b4b4b', edgecolor='white', loc='best', labelcolor='white')
    plt.grid(color='white',linestyle='--', linewidth=1)
    # 테두리 색상 설정
    for spine in plt.gca().spines.values():
        spine.set_edgecolor('white')
    plt.tight_layout()
    

    # 그래프를 PNG로 저장
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)  # PNG 형식으로 저장
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # PNG를 base64로 인코딩
    graph = base64.b64encode(image_png).decode('utf-8')



    context = {
        'stock': stock,
        'market_cap': market_cap,
        'current_price' : current_price,
        'dividend_date' :dividend_date,
        'last_dividend' :last_dividend,
        'dividend_yield' : dividend_yield,
        'summary': summary,
        'dividend_list': dividend_list,
        'stock_history_list': stock_history_list,
        'graph': graph
    }
    return render(request, "stocks/detail.html", context)
