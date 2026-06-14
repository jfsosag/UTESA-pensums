#!/bin/bash
set -e
echo "========================================="
echo "  Deploy UTESA Pensums a Fly.io"
echo "========================================="
echo ""

# 1. Verificar Fly CLI
if ! command -v fly &> /dev/null; then
    echo "[1/8] Instalando Fly CLI..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="$HOME/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
    echo 'export PATH="$HOME/.fly/bin:$PATH"' >> ~/.bashrc
else
    echo "[1/8] Fly CLI ya instalado"
fi

# 2. Login
echo "[2/8] Iniciando sesión en Fly.io..."
fly auth login

# 3. Subir código a GitHub (si no está ya)
echo "[3/8] Verificando conexión con GitHub..."
if ! git remote -v | grep -q origin; then
    git remote add origin https://github.com/jfsosag/UTESA-pensums.git
fi
git push -u origin master

# 4. Crear app en Fly
echo "[4/8] Creando app en Fly.io..."
fly launch --name utesa-pensums --no-deploy --region iad || true
# Si ya existe, ignora el error

# 5. Crear PostgreSQL
echo "[5/8] Creando base de datos PostgreSQL (gratis, 3GB)..."
fly postgres create --name utesa-pensums-db --region iad --initial-cluster-size free || true
# Si ya existe, ignora el error

# 6. Conectar PostgreSQL a la app
echo "[6/8] Conectando PostgreSQL a la app..."
fly postgres attach utesa-pensums-db --app utesa-pensums || true

# 7. Setear variables de entorno
echo "[7/8] Configurando variables de entorno..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || \
             docker run --rm python:3.13-slim python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || \
             echo "django-insecure-$(openssl rand -hex 32)")
fly secrets set --app utesa-pensums \
    SECRET_KEY="$SECRET_KEY" \
    DEBUG=False \
    ALLOWED_HOSTS=".fly.dev,localhost,127.0.0.1"

# 8. Desplegar
echo "[8/8] Desplegando..."
fly deploy --app utesa-pensums

echo ""
echo "========================================="
echo "  Despliegue completado!"
echo "========================================="
echo ""
echo "App:        https://utesa-pensums.fly.dev"
echo ""
echo "Próximo paso: migrar los datos locales"
echo "Ejecuta:"
echo "  python manage.py dumpdata --natural-foreign --natural-primary \\"
echo "    -e contenttypes -e auth.permission --output data_export.json"
echo "  fly postgres connect -a utesa-pensums-db"
echo "  DATABASE_URL=\"<URL_DE_CONEXION>\" python manage.py migrate"
echo "  DATABASE_URL=\"<URL_DE_CONEXION>\" python manage.py loaddata data_export.json"
echo ""
echo "O usa:"
echo "  fly ssh console -a utesa-pensums -C \"python manage.py migrate\""
echo "  fly ssh console -a utesa-pensums -C \"python manage.py createsuperuser\""
