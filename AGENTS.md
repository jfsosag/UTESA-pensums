# AGENTS.md - Contexto del proyecto UTESA Pensums

## Proyecto
App Django 5.1 desplegada en Render con PostgreSQL.
- URL: https://utesa-pensums.onrender.com
- Admin: https://utesa-pensums.onrender.com/admin/
- GitHub: https://github.com/jfsosag/UTESA-pensums
- Repo local: /home/jsosa/UTESA-pensums

## Estado actual
- ✅ App funcionando con PostgreSQL persistente
- ✅ 20 carreras con datos, 4 sin datos (Com. Social, Enfermería, Medicina, Nutrición)
- ✅ Admin accesible (admin / admin123)
- ⚠️ Build Command debe tener `flush` antes de `loaddata` para evitar duplicados:
  `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py flush --noinput && python manage.py loaddata data_export.json`
- ⚠️ Python 3.14 incompatible con Django 5.1. En Render se fijó `PYTHON_VERSION=3.13.3`

## Problemas conocidos
- Portadas de recintos: las URLs apuntan a `/media/` pero los archivos no están subidos a Render
- Medicina PDF (2024) y Nutrición Humana PDF son imagen (sin texto) — no se pueden extraer
- Sin PDFs para Comunicación Social y Enfermería
- Sleep de Render free tier: el web service se duerme a los 15 min, se despierta solo al recibir visita
- Contaduría Pública: el PDF estaba mal nombrado como "Enfermería" — ya corregido

## Sesión anterior
Ver Obsidian: "01 - Sesiones/Deploy a Render y persistencia de datos.md"

## Para continuar
- Extraer datos de carreras faltantes (Com. Social, Enfermería, Medicina, Nutrición)
- Agregar prerrequisitos desde PDFs
