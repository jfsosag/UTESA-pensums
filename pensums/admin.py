import csv
from io import TextIOWrapper
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.contrib import messages
from .models import Recinto, Carrera, Materia, Comentario


class MateriaInline(admin.TabularInline):
    model = Materia
    extra = 1
    fields = ["codigo", "nombre", "creditos", "semestre", "activo"]
    show_change_link = True
    fk_name = "carrera"


@admin.register(Recinto)
class RecintoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "activo", "fecha_creacion"]
    list_filter = ["activo"]
    prepopulated_fields = {"slug": ["nombre"]}
    search_fields = ["nombre"]
    filter_horizontal = ["carreras"]
    fieldsets = [
        (None, {"fields": ["nombre", "slug", "descripcion"]}),
        ("Imagen", {"fields": ["portada"]}),
        ("Carreras", {"fields": ["carreras"]}),
        ("Estado", {"fields": ["activo"]}),
    ]

    def get_list_display(self, request):
        return ["thumbnail_portada", "nombre", "activo", "fecha_creacion"]

    def thumbnail_portada(self, obj):
        if obj.portada:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;">',
                obj.portada.url,
            )
        return format_html(
            '<div style="width:60px;height:60px;border-radius:8px;background:linear-gradient(135deg,#003087,#C8102E);display:flex;align-items:center;justify-content:center;color:#fff;font-size:20px;font-weight:bold;">{}</div>',
            obj.nombre[0],
        )

    thumbnail_portada.short_description = "Portada"


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ["nombre", "codigo", "activo", "importar_csv_link"]
    list_filter = ["activo"]
    prepopulated_fields = {"slug": ["nombre"]}
    search_fields = ["nombre", "codigo"]
    inlines = [MateriaInline]

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:carrera_id>/importar-csv/",
                self.admin_site.admin_view(self.importar_csv_view),
                name="pensums_carrera_importar_csv",
            ),
        ]
        return custom + urls

    def importar_csv_link(self, obj):
        url = reverse("admin:pensums_carrera_importar_csv", args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="background:#003087;color:#fff;padding:3px 8px;border-radius:4px;font-size:11px;white-space:nowrap">📥 CSV</a>',
            url,
        )

    importar_csv_link.short_description = "Importar"

    def importar_csv_view(self, request, carrera_id):
        carrera = Carrera.objects.get(pk=carrera_id)

        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                messages.error(request, "Debes seleccionar un archivo CSV.")
                return redirect(request.path)

            if not csv_file.name.endswith(".csv"):
                messages.error(request, "El archivo debe tener extensión .csv")
                return redirect(request.path)

            creadas = 0
            actualizadas = 0
            errores = []

            try:
                reader = csv.DictReader(TextIOWrapper(csv_file, encoding="utf-8"))
                if not reader.fieldnames:
                    messages.error(request, "El CSV está vacío o sin cabeceras.")
                    return redirect(request.path)

                cols = set(reader.fieldnames)
                req = {"codigo", "nombre", "creditos", "semestre"}
                if not req.issubset(cols):
                    faltan = req - cols
                    messages.error(request, f"Faltan columnas: {', '.join(sorted(faltan))}")
                    return redirect(request.path)

                for fila_num, row in enumerate(reader, start=2):
                    try:
                        codigo = row["codigo"].strip()
                        nombre = row["nombre"].strip()
                        creditos = int(row["creditos"])
                        semestre = str(int(row["semestre"]))
                        if semestre not in [str(i) for i in range(1, 13)]:
                            errores.append(f"Fila {fila_num}: semestre inválido")
                            continue
                        _, created = Materia.objects.update_or_create(
                            carrera=carrera,
                            codigo=codigo,
                            defaults={
                                "nombre": nombre,
                                "creditos": creditos,
                                "semestre": semestre,
                            },
                        )
                        if created:
                            creadas += 1
                        else:
                            actualizadas += 1
                    except (ValueError, KeyError) as e:
                        errores.append(f"Fila {fila_num}: {e}")

                if creadas or actualizadas:
                    messages.success(
                        request,
                        f"✅ {creadas} creadas, {actualizadas} actualizadas para {carrera.nombre}.",
                    )
                if errores:
                    messages.warning(request, f"⚠️ {len(errores)} error(es): {'; '.join(errores[:5])}")

            except Exception as e:
                messages.error(request, f"Error al leer CSV: {e}")

            return redirect(reverse("admin:pensums_carrera_changelist"))

        ctx = {
            **self.admin_site.each_context(request),
            "title": f"Importar CSV - {carrera.nombre}",
            "carrera": carrera,
            "opts": self.model._meta,
        }
        return render(request, "admin/pensums/importar_csv.html", ctx)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ["codigo", "nombre", "carrera", "semestre", "creditos", "activo", "lista_prerrequisitos"]
    list_filter = ["carrera", "semestre", "activo"]
    search_fields = ["codigo", "nombre"]
    list_editable = ["activo"]
    list_select_related = ["carrera"]
    filter_horizontal = ["prerrequisitos", "corequisitos"]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ["materia", "nombre_profesor", "numero_grupo", "fecha_creacion", "activo"]
    list_filter = ["activo", "materia__carrera"]
    search_fields = ["nombre_profesor", "comentario"]
    list_editable = ["activo"]
    list_select_related = ["materia"]
    actions = ["aprobar_seleccionados", "desactivar_seleccionados"]

    @admin.action(description="✅ Aprobar comentarios seleccionados")
    def aprobar_seleccionados(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f"{updated} comentario(s) aprobado(s).")

    @admin.action(description="❌ Desactivar comentarios seleccionados")
    def desactivar_seleccionados(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f"{updated} comentario(s) desactivado(s).")
