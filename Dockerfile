FROM python:3.9-alpine
WORKDIR /apps/pynball/
COPY src/pynball/. .
COPY requirements/development.txt .
RUN ["pip", "install", "-r", "development.txt"]
CMD ["python", "pynball.py"]
