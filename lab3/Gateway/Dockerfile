FROM python:3.9
COPY main.py /app/
COPY requirements.txt /app/
WORKDIR /app
EXPOSE 8080
RUN pip install -r requirements.txt
CMD ["python3", "/app/main.py"]