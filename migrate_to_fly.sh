#!/bin/bash
# Migra datos desde SQLite local a PostgreSQL en Fly.io
# Uso: ./migrate_to_fly.sh <DATABASE_URL>
set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <DATABASE_URL>"
    echo ""
    echo "Para obtener DATABASE_URL:"
    echo "  fly postgres connect -a utesa-pensums-db -C"
    echo ""
    exit 1
fi

DATABASE_URL="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "1. Exportando datos desde SQLite..."
python3 manage.py dumpdata --natural-foreign --natural-primary \
    -e contenttypes -e auth.permission \
    --output /tmp/data_export.json
echo "   OK: $(du -h /tmp/data_export.json | cut -f1)"

echo "2. Corriendo migraciones en PostgreSQL..."
DATABASE_URL="$DATABASE_URL" python3 manage.py migrate

echo "3. Cargando datos..."
DATABASE_URL="$DATABASE_URL" python3 manage.py loaddata /tmp/data_export.json

echo "4. Creando superusuario admin/admin123..."
DATABASE_URL="$DATABASE_URL" python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@utesa.edu', 'admin123')
    print('Superusuario admin creado')
else:
    print('Superusuario admin ya existe')
"

echo ""
echo "Migración completada. Datos ahora en PostgreSQL de Fly.io!"
