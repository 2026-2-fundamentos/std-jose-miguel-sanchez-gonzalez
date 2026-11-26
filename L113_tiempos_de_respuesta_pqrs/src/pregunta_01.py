import pandas as pd
import numpy as np
from pathlib import Path

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_web = directorio_actual.parent / "data" / "historical_requests_web.csv.gz"
    ruta_cartas = directorio_actual.parent / "data" / "historical_requests_letter.csv.gz"
    ruta_channel_summary = directorio_actual.parent / "submission" / "channel_summary.csv"
    ruta_yearly_summary = directorio_actual.parent / "submission" / "yearly_summary.csv"
    ruta_entry_day_summary = directorio_actual.parent / "submission" / "entry_day_summary.csv"
    
    # 1. Leer archivos y eliminar filas idénticas dentro de cada canal
    df_web = pd.read_csv(ruta_web, sep=",").drop_duplicates().copy()
    df_web["channel"] = "web"

    df_letter = pd.read_csv(ruta_cartas, sep=",").drop_duplicates().copy()
    df_letter["channel"] = "letter"

    df = pd.concat([df_web, df_letter], ignore_index=True)

    # 2. Conversión de fechas e identificación de solicitudes respondidas vs. pendientes
    in_dt = pd.to_datetime(df["in_date"])
    out_dt = pd.to_datetime(df["out_date"])

    df["year"] = in_dt.dt.year
    df["is_answered"] = out_dt.notna()

    # Días calendario: diferencia entre fecha de respuesta y fecha de entrada
    df["calendar_days"] = (out_dt - in_dt).dt.days

    # Días hábiles: lunes a viernes posteriores a in_dt hasta out_dt incluida.
    # np.busday_count(A, B) cuenta días hábiles en [A, B).
    # Sumar 1 día a ambas fechas desplaza el intervalo a [A + 1 día, B + 1 día),
    # lo que equivale exactamente a los días hábiles en (in_dt, out_dt].
    answered_mask = df["is_answered"]
    in_dates_next = (in_dt[answered_mask] + pd.Timedelta(days=1)).values.astype(
        "datetime64[D]"
    )
    out_dates_next = (out_dt[answered_mask] + pd.Timedelta(days=1)).values.astype(
        "datetime64[D]"
    )

    df["business_days"] = np.nan
    df.loc[answered_mask, "business_days"] = np.busday_count(
        in_dates_next, out_dates_next
    )

    # Cumplimiento del plazo: respondida en <= 15 días hábiles (pendientes = False)
    df["on_time"] = df["is_answered"] & (df["business_days"] <= 15)

    # ---------------------------------------------------------
    # 3. Tabla 1: channel_summary.csv
    # ---------------------------------------------------------
    channel_summary = (
        df.groupby("channel", as_index=False)
        .agg(
            requests=("channel", "count"),
            answered=("is_answered", "sum"),
            pending=("is_answered", lambda s: int((~s).sum())),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values("channel")
        .reset_index(drop=True)
    )
    channel_summary["answered"] = channel_summary["answered"].astype(int)

    # ---------------------------------------------------------
    # 4. Tabla 2: yearly_summary.csv
    # ---------------------------------------------------------
    yearly_summary = (
        df.groupby(["year", "channel"], as_index=False)
        .agg(
            requests=("channel", "count"),
            pending=("is_answered", lambda s: int((~s).sum())),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 5. Tabla 3: entry_day_summary.csv
    # ---------------------------------------------------------
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    # Detectar si day_name en el archivo viene en español o en inglés
    sample_days = set(df["day_name"].dropna().unique())
    if {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes"} & sample_days:
        day_order = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]

    entry_day_summary = (
        df.groupby("day_name", as_index=False)
        .agg(
            requests=("day_name", "count"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .set_index("day_name")
        .reindex(day_order)
        .reset_index()
    )

    # ---------------------------------------------------------
    # 6. Guardar CSVs sin índice y retornar las tres tablas
    # ---------------------------------------------------------
    channel_summary.to_csv(ruta_channel_summary, index=False)
    yearly_summary.to_csv(ruta_yearly_summary, index=False)
    entry_day_summary.to_csv(ruta_entry_day_summary, index=False)

    return channel_summary, yearly_summary, entry_day_summary
