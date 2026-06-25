FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/shared/python:/app
COPY template-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/python ./shared/python
COPY template-service/app ./app
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
