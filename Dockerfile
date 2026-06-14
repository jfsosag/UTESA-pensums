# Usa Python oficial
FROM python:3.13-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependencias del sistema necesarias para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto
COPY . .

# Recolecta archivos estáticos
RUN python manage.py collectstatic --noinput

# Expone el puerto
EXPOSE 8000

# Arranca con gunicorn
CMD ["gunicorn", "utesa_pensums.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
