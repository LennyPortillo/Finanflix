## Finanflix Lenny Portillo - Análisis de compras y suscripciones

Este script procesa un archivo CSV de ventas y genera un Excel con métricas por usuario para responder:

- **Tiempo en la suscripción antes de comprar un programa individual**.
- **Tiempo hasta que compró la siguiente suscripción**.

### Qué hace el script

Entrada esperada: un CSV llamado `ventas.csv` en la misma carpeta del script, con estas columnas:

- `Correo electronico`
- `Fecha` (formato de fecha reconocible, p. ej. `YYYY-MM-DD` o `DD/MM/YYYY`)
- `Producto` (texto con el nombre del producto)

Clasificación de productos (detecta por texto en `Producto`, sin distinguir mayúsculas/minúsculas):

- Free trial → `Free trial`
- Suscripción FF mensual → `Suscripción FF`
- `Trimestral`, `Semestral`, `Anual`
- Todo lo demás → `Programa individual`
- Se excluyen filas que contengan "beca" en `Producto`.

Métricas calculadas por usuario:

- `Dias_activo_total`: días sumados de suscripciones (según duración de cada plan).
- `Dias_desde_alta_a_prog_individual`: días desde la primera compra del usuario hasta su primera compra de programa individual.
- `Dias_hasta_recompra`: diferencia entre el vencimiento de la última suscripción y la compra de programa individual (si aplica).

El resultado se guarda como `resumen_usuarios.xlsx` en esta misma carpeta.

### Requisitos

- Windows 10 o superior.
- Python recomendado: **3.11 o 3.12**.
  - Nota: Si usas Python 3.14 y alguna librería aún no tiene soporte, usa 3.12.

### Instalación (una sola vez)

Opción A: Usando `requirements.txt` (recomendado)

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Opción B: Instalar paquetes manualmente

```powershell
python -m pip install --upgrade pip
pip install pandas numpy openpyxl
```

Si tienes varias versiones de Python, activa un entorno virtual:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

### Cómo usarlo (cada vez que haya un CSV nuevo)

1. Colocar el archivo CSV llamado `ventas.csv` en esta carpeta: `Analitycs/Script Finalizado/`.
   - Si tu archivo tiene otro nombre, renómbralo a `ventas.csv` o edita el script para apuntar al nombre correcto.
2. Abrir PowerShell en esta carpeta.
3. Ejecutar:

```powershell
python ".\Analitycs_compra_programaind.py"
```

4. Al finalizar, se generará `resumen_usuarios.xlsx` en la misma carpeta. Ese es el archivo que deben abrir/compartir.

### Personalizaciones rápidas (si hiciera falta)

- Separador del CSV: el script usa coma por defecto (`sep=','`). Si tu CSV usa `;`, abre el script y cambia a `sep=';'` en la línea de lectura de `ventas.csv`.
- Codificación: por defecto `encoding='utf-8'`. Si alguna tilde sale mal, prueba `encoding='latin-1'`.
- Nombre del archivo: si no quieren renombrar el CSV, cambien `'ventas.csv'` por el nombre real en la línea de lectura.

### Errores comunes y soluciones

- `ModuleNotFoundError: No module named 'pandas'`: Faltan dependencias. Ejecuta la sección de Instalación.
- Columnas no encontradas: Verifica que el CSV tenga exactamente `Correo electronico`, `Fecha`, `Producto`.
- Fechas no se parsean: Confirma el formato de fechas del CSV. Si es necesario, normaliza previamente el formato a `YYYY-MM-DD`.

### Salida esperada

Archivo `resumen_usuarios.xlsx` con, entre otras, estas columnas por usuario:

- `Correo electronico`
- `Primera_fecha_alta`
- `Ultima_fecha_actividad`
- `Dias_activo_total`
- `Compro_programa_individual`
- `Dias_desde_alta_a_prog_individual`
- `Dias_hasta_recompra`

Si necesitan métricas adicionales o ajustes en las definiciones, indíquenlo y se adaptan las reglas de cálculo.


