from django.test import TestCase, Client
from django.urls import reverse
from pensums.models import Recinto, Carrera, Materia, Comentario


class ModelosTests(TestCase):
    def setUp(self):
        self.recinto = Recinto.objects.create(
            nombre="Recinto Santiago",
            slug="recinto-santiago",
        )
        self.carrera = Carrera.objects.create(
            nombre="Ingeniería en Sistemas",
            slug="ingenieria-en-sistemas",
            codigo="IS-01",
        )
        self.recinto.carreras.add(self.carrera)
        self.materia = Materia.objects.create(
            carrera=self.carrera,
            codigo="PRO101",
            nombre="Programación I",
            creditos=3,
            semestre="1",
        )
        self.comentario = Comentario.objects.create(
            materia=self.materia,
            numero_grupo=1,
            nombre_profesor="Juan Pérez",
            comentario="Excelente materia",
        )

    def test_recinto_str(self):
        self.assertEqual(str(self.recinto), "Recinto Santiago")

    def test_carrera_str(self):
        self.assertEqual(str(self.carrera), "Ingeniería en Sistemas")

    def test_materia_str(self):
        self.assertIn("PRO101", str(self.materia))
        self.assertIn("Programación I", str(self.materia))

    def test_comentario_str(self):
        self.assertIn("PRO101", str(self.comentario))
        self.assertIn("Juan Pérez", str(self.comentario))

    def test_cantidad_carreras(self):
        self.assertEqual(self.recinto.cantidad_carreras(), 1)

    def test_cantidad_materias(self):
        self.assertEqual(self.carrera.cantidad_materias(), 1)

    def test_total_creditos(self):
        self.assertEqual(self.carrera.total_creditos(), 3)

    def test_prerrequisitos(self):
        materia2 = Materia.objects.create(
            carrera=self.carrera,
            codigo="PRO102",
            nombre="Programación II",
            creditos=3,
            semestre="2",
        )
        materia2.prerrequisitos.add(self.materia)
        self.assertEqual(materia2.prerrequisitos.count(), 1)
        self.assertIn(self.materia, materia2.prerrequisitos.all())

    def test_corequisitos(self):
        lab = Materia.objects.create(
            carrera=self.carrera,
            codigo="LAB101",
            nombre="Laboratorio",
            creditos=1,
            semestre="1",
        )
        self.materia.corequisitos.add(lab)
        self.assertEqual(self.materia.corequisitos.count(), 1)
        self.assertIn(lab, self.materia.corequisitos.all())

    def test_recinto_carreras_m2m(self):
        self.assertIn(self.carrera, self.recinto.carreras.all())

    def test_carrera_recintos_reverse(self):
        self.assertIn(self.recinto, self.carrera.recintos.all())


class VistasTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.recinto = Recinto.objects.create(
            nombre="Recinto Santiago",
            slug="recinto-santiago",
        )
        self.carrera = Carrera.objects.create(
            nombre="Ingeniería en Sistemas",
            slug="ingenieria-en-sistemas",
        )
        self.recinto.carreras.add(self.carrera)
        self.materia = Materia.objects.create(
            carrera=self.carrera,
            codigo="PRO101",
            nombre="Programación I",
            creditos=3,
            semestre="1",
        )

    def test_inicio_200(self):
        response = self.client.get(reverse("pensums:inicio"))
        self.assertEqual(response.status_code, 200)

    def test_recinto_200(self):
        response = self.client.get(
            reverse("pensums:recinto", kwargs={"slug": self.recinto.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_carrera_200(self):
        response = self.client.get(
            reverse("pensums:carrera", kwargs={
                "recinto_slug": self.recinto.slug,
                "carrera_slug": self.carrera.slug,
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_materia_200(self):
        response = self.client.get(
            reverse("pensums:materia", kwargs={
                "recinto_slug": self.recinto.slug,
                "carrera_slug": self.carrera.slug,
                "pk": self.materia.pk,
            })
        )
        self.assertEqual(response.status_code, 200)

    def test_recinto_404(self):
        response = self.client.get(
            reverse("pensums:recinto", kwargs={"slug": "no-existe"})
        )
        self.assertEqual(response.status_code, 404)

    def test_materia_muestra_carrera_recinto(self):
        url = reverse("pensums:materia", kwargs={
            "recinto_slug": self.recinto.slug,
            "carrera_slug": self.carrera.slug,
            "pk": self.materia.pk,
        })
        response = self.client.get(url)
        self.assertContains(response, self.materia.nombre)


class FormularioTests(TestCase):
    def setUp(self):
        self.client = Client()
        recinto = Recinto.objects.create(
            nombre="Recinto Santiago",
            slug="recinto-santiago",
        )
        carrera = Carrera.objects.create(
            nombre="Ingeniería en Sistemas",
            slug="ingenieria-en-sistemas",
        )
        recinto.carreras.add(carrera)
        self.materia = Materia.objects.create(
            carrera=carrera,
            codigo="PRO101",
            nombre="Programación I",
            creditos=3,
            semestre="1",
        )
        self.recinto = recinto
        self.carrera = carrera

    def test_comentario_valido(self):
        response = self.client.post(
            reverse("pensums:crear_comentario", kwargs={
                "recinto_slug": self.recinto.slug,
                "carrera_slug": self.carrera.slug,
                "pk": self.materia.pk,
            }),
            {
                "numero_grupo": 2,
                "nombre_profesor": "María García",
                "comentario": "Buena materia, muy recomendada",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comentario.objects.count(), 1)

    def test_comentario_invalido_sin_nombre(self):
        response = self.client.post(
            reverse("pensums:crear_comentario", kwargs={
                "recinto_slug": self.recinto.slug,
                "carrera_slug": self.carrera.slug,
                "pk": self.materia.pk,
            }),
            {
                "numero_grupo": 2,
                "nombre_profesor": "",
                "comentario": "Comentario sin profesor",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comentario.objects.count(), 0)
