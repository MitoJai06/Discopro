# Patrones de seguridad aplicados en AppDiscopro

Patrones detectados y su finalidad
1. Protección CSRF
   - Qué hace: evita peticiones POST forjadas desde sitios externos.
   - Dónde: todas las plantillas con formularios incluyen `{% csrf_token %}`.
   - Ejemplo: plantilla `motorista/form.html` contiene:
     ```django
     <form method="post" novalidate>
         {% csrf_token %}
         ...
     </form>
     ```
   - Recomendación: mantener CSRF activado en middleware (ya está en settings).

2. Validación del lado servidor (ModelForm)
   - Qué hace: valida y sanitiza los datos antes de persistirlos.
   - Dónde: formularios definidos en `AppDiscopro/forms.py` y comprobados en vistas con `form.is_valid()`.
   - Ejemplo (vista): `despacho_directo_create` en `AppDiscopro/views.py`:
     ```python
     form = DespachoDirectoForm(request.POST)
     if form.is_valid():
         despacho = form.save(commit=False)
         despacho.save()
     ```
   - Recomendación: añadir validaciones específicas en `clean()` según reglas de negocio.

3. Uso del ORM (protección contra SQL Injection)
   - Qué hace: construye consultas parametrizadas evitando concatenación manual.
   - Dónde: en consultas como `Despacho.objects.filter(...)`, `select_related(...)`.
   - Ejemplo:
     ```python
     despachos = Despacho.objects.filter(fecha_creacion__date=fecha_obj)
     ```
   - Recomendación: evitar `raw()` sin parametrizar.

4. Manejo de recursos inexistentes con get_object_or_404
   - Qué hace: evita exponer tracebacks y controla acceso a recursos no presentes.
   - Dónde: `get_object_or_404(Farmacia, codigo_farmacia=pk)` en `views.py`.
   - Ejemplo:
     ```python
     farmacia = get_object_or_404(Farmacia, codigo_farmacia=pk)
     ```

5. Control de estado y reglas de negocio en vistas
   - Qué hace: evita cambios inválidos (ej.: no modificar despachos finalizados/cancelados).
   - Dónde: `despacho_update` valida `despacho.estado`.
   - Ejemplo:
     ```python
     if despacho.estado in ['FINALIZADO', 'CANCELADO']:
         messages.error(request, 'No se puede modificar...')
         return redirect(...)
     ```

6. Constraints en modelos (integridad)
   - Qué hace: evita duplicados y mantiene consistencia (unique, unique_together).
   - Dónde: `models.py` (ej. `DocumentacionMoto.unique_together`).
   - Recomendación: añadir migraciones/constraints adicionales cuando aplique.

7. Feedback seguro (messages)
   - Qué hace: comunica resultados al usuario sin exponer información sensible.
   - Dónde: uso de `messages.success`, `messages.error` en vistas.

8. Buenas prácticas detectadas
   - `select_related` usado para reducir consultas y no exponer relaciones innecesarias.
   - Plantilla base con manejo de `messages` y carga de `static`.
   - Notas de seguridad en `settings.py` sobre `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.

Ejemplos de ubicaciones concretas
- Vistas y validación: `AppDiscopro/views.py` (vistas CRUD, forms.is_valid, get_object_or_404)
- Formularios y widgets: `AppDiscopro/forms.py` (ModelForm centraliza validación)
- Modelos y constraints: `AppDiscopro/models.py` (unique_together, ForeignKey on_delete)
- Plantillas (CSRF): `templates/*/*.html` (todos los formularios POST incluyen `{% csrf_token %}`)
- Configuración sensible: `prjDiscopro/settings.py` (SECRET_KEY, DEBUG, DB creds) — revisar para producción.


