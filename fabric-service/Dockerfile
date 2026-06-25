FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/shared/python:/app
COPY fabric-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/python ./shared/python
COPY fabric-service/app ./app
EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
