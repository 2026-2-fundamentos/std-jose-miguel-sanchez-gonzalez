import json
import os
import re
from pathlib import Path
import pandas as pd

def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "ventas.csv.gz"
    ruta_salida = directorio_actual.parent / "submission" / "data_quality_report.json"
    # 1. Leer el archivo como texto crudo (dtype=str) y sin parsear NAs automáticamente
    # para conservar los valores exactamente como aparecen en el archivo.
    # encoding="utf-8-sig" elimina automáticamente la marca BOM si existe.
    df = pd.read_csv(
        ruta_entrada,
        compression="gzip",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    # 2. Normalizar encabezados:
    # eliminar BOM residual (\ufeff), quitar espacios inicio/fin, pasar a minúsculas
    # y reemplazar espacios internos por '_'
    df.columns = [
        re.sub(r"\s+", "_", col.lstrip("\ufeff").strip().lower())
        for col in df.columns
    ]

    columnas_requeridas = [
        "supplier_id",
        "supplier",
        "country",
        "city",
        "purchase_date",
        "amount",
        "discount",
        "weight",
        "units",
        "unit_price",
        "contact_email",
    ]

    # Columnas faltantes e inesperadas (ordenadas)
    set_actuales = set(df.columns)
    set_requeridas = set(columnas_requeridas)

    missing_required_columns = sorted(list(set_requeridas - set_actuales))
    unexpected_columns = sorted(list(set_actuales - set_requeridas))

    # 3. Conteos de filas, columnas y duplicados
    row_count = int(len(df))
    column_count = int(len(df.columns))
    duplicate_row_count = int(df.duplicated(keep="first").sum())

    if "supplier_id" in df.columns:
        # keep=False marca TODAS las apariciones de los supplier_id que se repiten
        duplicate_supplier_id_row_count = int(
            df["supplier_id"].duplicated(keep=False).sum()
        )
    else:
        duplicate_supplier_id_row_count = 0

    # 4. Valores faltantes por columna (celdas vacías "" o exactamente "N/A")
    # Nota: se evalúa sin alterar los espacios internos/externos de los datos,
    # considerando vacío ("") o "N/A"
    missing_value_count_by_column = {}
    for col in df.columns:
        es_faltante = df[col].isin(["", "N/A"])
        missing_value_count_by_column[col] = int(es_faltante.sum())

    # 5. Validación de contact_email (forma usuario@dominio.extension)
    if "contact_email" in df.columns:
        patron_email = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        emails_validos = df["contact_email"].str.match(patron_email, na=False)
        invalid_email_count = int((~emails_validos).sum())
    else:
        invalid_email_count = 0

    # 6. Validación de units:
    # "cantidad de valores numéricos de `units` que no son enteros positivos.
    # Los valores faltantes no se cuentan aquí."
    if "units" in df.columns:
        no_faltantes = df.loc[~df["units"].isin(["", "N/A"]), "units"]
        # Intentar convertir a numérico para filtrar solo los que son valores numéricos
        numericos = pd.to_numeric(no_faltantes, errors="coerce").dropna()
        # Un entero positivo debe ser > 0 y no tener parte decimal (numericos % 1 == 0)
        es_entero_positivo = (numericos > 0) & (numericos % 1 == 0)
        invalid_unit_count = int((~es_entero_positivo).sum())
    else:
        invalid_unit_count = 0

    # 7. Valores distintos de country (ordenados y escritos exactamente como aparecen)
    if "country" in df.columns:
        # Se excluyen faltantes si aplica o se toman todos los distintos de la columna:
        # Si quieres incluir todos los valores tal cual aparecen (sin filtrar N/A):
        valores_country = df.loc[~df["country"].isin(["", "N/A"]), "country"].unique().tolist()
        country_values = sorted(valores_country)
    else:
        country_values = []

    # 8. Construir diccionario de reporte
    reporte = {
        "row_count": row_count,
        "column_count": column_count,
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    # 9. Escribir el archivo JSON asegurando que el directorio exista
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=4, ensure_ascii=False)

    return reporte
  
#main()
