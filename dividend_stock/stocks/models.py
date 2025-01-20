from django.db import models

class Ticker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # 티커 심볼
    market = models.CharField(max_length=100, null=True, blank=True)  # 시장

    def __str__(self):
        return self.symbol

class DividendTicker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # 티커 심볼
    market = models.CharField(max_length=100, null=True, blank=True)  # 시장
    checked_at = models.DateTimeField(auto_now_add=True)  # 확인 날짜

    def __str__(self):
        return self.symbol
    
    # models.py
from django.db import models

class CollectedDividendData(models.Model):
    ticker = models.CharField(max_length=10, unique=True)  # 티커 심볼
    current_price = models.FloatField(null=True, blank=True)  # 현재 주가
    last_dividend = models.FloatField(null=True, blank=True)  # 마지막 배당금
    dividend_date = models.CharField(max_length=100, null=True, blank=True)  # 배당일
    dividend_yield = models.FloatField(null=True, blank=True)  # 배당률
    market_cap = models.CharField(max_length=50, null=True, blank=True)  # 시가총액
    dividend_yield_category = models.CharField(
        max_length=20, choices=[("4_to_7", "4~7%"), ("above_7", "7% 이상")], null=True
    )  # 배당률 범주

    def __str__(self):
        return f"{self.ticker} - {self.dividend_yield_category}"
