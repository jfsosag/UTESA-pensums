#!/bin/bash
# Carga datos exportados a PostgreSQL
# Uso: ./import_data_postgres.sh <DATABASE_URL>
set -e
cd "$(dirname "$0")"
source .venv/bin/activate

if [ -z "$1" ]; then
    echo "Uso: $0 <DATABASE_URL>"
    echo "Ej: $0 postgres://user:pass@host:5432/utesa_pensums"
    exit 1
fi

export DATABASE_URL="$1"

echo "Corriendo migraciones..."
python manage.py migrate

echo "Cargando datos..."
python manage.py loaddata data_export.json

echo "Creando superusuario (admin/admin123)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@utesa.edu', 'admin123')
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
"

echo "Listo. Recolectando staticfiles..."
python manage.py collectstatic --noinput
echo "OK. Todo listo para producción."