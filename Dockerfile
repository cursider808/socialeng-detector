FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python data_factory.py && python ml_model.py

EXPOSE 8000
CMD ["python", "app.py", "--mode", "web", "--host", "0.0.0.0", "--port", "8000"]
