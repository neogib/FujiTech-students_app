FROM python:3.9-slim

# Ustawiamy katalog roboczy w kontenerze dla backendu
WORKDIR /app/backend

# Kopiujemy cały kod backendu
COPY backend/ .

# Instalujemy pip (aktualizacja), następnie instalujemy uv i synchronizujemy zależności
RUN pip install --upgrade pip && pip install uv && uv sync --project .

# Informujemy, że aplikacja będzie korzystać z portu 8000
EXPOSE 8000

# Uruchamiamy aplikację przy pomocy uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
