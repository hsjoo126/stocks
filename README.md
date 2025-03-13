# EasyFinance
# Project : EasyFinance
미국 고배당주를 한 눈에 볼 수 있는, 초보자들을 위한 주식 정보 제공 사이트

## Project Introduction
실제 배당주 투자를 하면서 고배당주 정보를 한눈에 정리해둔 사이트가 없었습니다.<br>
저처럼, 배당주 투자에 관심 있는 초보자들이 각 종목의 배당정보를<br>
쉽게 확인할 수 있는 서비스가 필요하다고 느껴 개발하게 되었습니다.

## Development time
2025.01 ~ 2025.02 

## Development Environment
- **Programming Language:** Python 3.10  
- **Framework:** Django  
- **Database:** PostgreSQL, Redis  
- **Deployment:** AWS (EC2), Docker Compose, Nginx, Ubuntu  
- **Version Control:** Git, GitHub  
- **Task Scheduling:** Django-crontab  
- **Data Visualization:** Matplotlib  


## Deployment
hsjoo.site

## Installation
1. 깃허브 클론
```
https://github.com/hsjoo126/stocks
```
2. docker 실행
```
docker-compose build
docker-compose up
```
3. Django migration 진행
```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```


## API Documentation
![image](https://github.com/user-attachments/assets/5a6f2ce1-c64a-4036-8a27-034b4b3a5b4d)



## Apps Description
### stocks
- yfinance, FDR를 활용한 주식 정보 수집 및 제공
- Matplotlib으로 주가 흐름 시각화
- crontab을 활용해 정보 수집 자동화



## ERD
![image](https://github.com/user-attachments/assets/e559a892-2620-45c0-8cad-df11f2a07f6d)
