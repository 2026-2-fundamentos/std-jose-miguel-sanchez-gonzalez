from pathlib import Path
import pandas as pd
import re

def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "clusters_report.txt"

    with open(ruta_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()

    # Omitimos las primeras 4 líneas (encabezados y línea separadora)
    cuerpo = lineas[4:]

    registros = []
    registro_actual = None

    # Expresión regular para detectar el inicio de un clúster:
    # grupo 1: cluster | grupo 2: cantidad | grupo 3: porcentaje | grupo 4: inicio de palabras clave
    patron_inicio = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s+(.*)$")

    for linea in cuerpo:
        # Saltar líneas completamente en blanco
        if not linea.strip():
            continue

        coincidencia = patron_inicio.match(linea)
        if coincidencia:
            # Si ya estábamos construyendo un registro previo, lo guardamos
            if registro_actual:
                registros.append(registro_actual)

            cluster = int(coincidencia.group(1))
            cantidad = int(coincidencia.group(2))
            porcentaje = float(coincidencia.group(3).replace(",", "."))
            palabras = coincidencia.group(4).strip()

            registro_actual = {
                "cluster": cluster,
                "cantidad_de_palabras_clave": cantidad,
                "porcentaje_de_palabras_clave": porcentaje,
                "principales_palabras_clave": palabras,
            }
        elif registro_actual:
            # Si la línea no inicia un nuevo clúster, es continuación de las palabras clave
            registro_actual["principales_palabras_clave"] += " " + linea.strip()

    # Agregar el último registro procesado
    if registro_actual:
        registros.append(registro_actual)

    df = pd.DataFrame(registros)

    # Normalizar los espacios: reemplazar múltiples espacios por uno solo,
    # asegurar una coma y un único espacio entre palabras clave y quitar el punto final
    df["principales_palabras_clave"] = (
        df["principales_palabras_clave"]
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"\s*,\s*", ", ", regex=True)
        .str.rstrip(".")
        .str.strip()
    )

    return df
