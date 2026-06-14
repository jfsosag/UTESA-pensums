#!/bin/bash
# Exporta datos de SQLite a JSON para cargar en PostgreSQL
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
echo "Exportando datos desde SQLite..."
python manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.permission \
  --output data_export.json
echo "OK: data_export.json generado ($(du -h data_export.json | cut -f1))"