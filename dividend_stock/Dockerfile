# Django Dockerfile
FROM python:3.10.11

# 프로젝트 작업 디렉터리
WORKDIR /app

# 프로젝트 요구사항 파일 복사 및 설치
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y python3-pip cron fonts-nanum && \
    pip install --no-cache-dir -r requirements.txt



# 프로젝트 파일 복사
COPY . /app/


# 포트
EXPOSE 8000

# 장고 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
