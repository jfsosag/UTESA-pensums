from django.db import migrations, models


def migrar_recinto_a_m2m(apps, schema_editor):
    Carrera = apps.get_model("pensums", "Carrera")
    for carrera in Carrera.objects.all():
        recinto_id = getattr(carrera, "recinto_id", None)
        if recinto_id is not None:
            carrera.recintos.add(recinto_id)


class Migration(migrations.Migration):

    dependencies = [
        ("pensums", "0003_remove_recinto_imagen_recinto_portada"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="carrera",
            options={
                "ordering": ["nombre"],
                "verbose_name": "Carrera",
                "verbose_name_plural": "Carreras",
            },
        ),
        migrations.AddField(
            model_name="recinto",
            name="carreras",
            field=models.ManyToManyField(
                blank=True,
                related_name="recintos",
                to="pensums.carrera",
                verbose_name="Carreras que se ofrecen",
            ),
        ),
        migrations.RunPython(migrar_recinto_a_m2m, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="carrera",
            name="recinto",
        ),
    ]
