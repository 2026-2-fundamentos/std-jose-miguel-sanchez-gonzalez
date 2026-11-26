import pandas as pd
from pathlib import Path

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "flights_by_carrier_day_hour.csv.gz"
    ruta_hourly = directorio_actual.parent / "submission" / "hourly_delay_rates.csv"
    ruta_carrier = directorio_actual.parent / "submission" / "carrier_adjusted_delays.csv"

    df = pd.read_csv(ruta_entrada, sep=",")
    
    # ---------------------------------------------------------
    # 1. Tabla: hourly_delay_rates.csv (una fila por hora, 0 a 23)
    # ---------------------------------------------------------
    hourly_delay_rates = (
        df.groupby("scheduled_departure_hour", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        )
        .sort_values("scheduled_departure_hour")
        .reset_index(drop=True)
    )
    hourly_delay_rates["delay_rate"] = (
        hourly_delay_rates["delayed_departure_15_flights"]
        / hourly_delay_rates["operated_flights"]
    )

    # ---------------------------------------------------------
    # 2. Tabla: carrier_adjusted_delays.csv
    # ---------------------------------------------------------
    # Agregar vuelos por aerolínea y hora para multiplicar por la tasa nacional horaria
    carrier_hour = df.groupby(
        ["reporting_airline", "scheduled_departure_hour"], as_index=False
    ).agg(
        operated_flights=("operated_flights", "sum"),
        delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
    )

    carrier_hour = carrier_hour.merge(
        hourly_delay_rates[["scheduled_departure_hour", "delay_rate"]].rename(
            columns={"delay_rate": "national_hourly_rate"}
        ),
        on="scheduled_departure_hour",
        how="left",
    )

    carrier_hour["expected_delayed_flights"] = (
        carrier_hour["operated_flights"] * carrier_hour["national_hourly_rate"]
    )

    # Consolidar totales por aerolínea
    carrier_summary = carrier_hour.groupby("reporting_airline", as_index=False).agg(
        operated_flights=("operated_flights", "sum"),
        delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        expected_delayed_flights=("expected_delayed_flights", "sum"),
    )

    # Filtrar aerolíneas con al menos 100,000 vuelos operados
    carrier_summary = carrier_summary[
        carrier_summary["operated_flights"] >= 100_000
    ].copy()

    # Tasas y razón observado / esperado
    carrier_summary["delay_rate"] = (
        carrier_summary["delayed_departure_15_flights"]
        / carrier_summary["operated_flights"]
    )
    carrier_summary["observed_to_expected_ratio"] = (
        carrier_summary["delayed_departure_15_flights"]
        / carrier_summary["expected_delayed_flights"]
    )

    # Rankings (1 = peor aerolínea, es decir, mayor tasa/razón)
    carrier_summary["crude_rank"] = (
        carrier_summary["delay_rate"].rank(ascending=False, method="min").astype(int)
    )
    carrier_summary["adjusted_rank"] = (
        carrier_summary["observed_to_expected_ratio"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    # Ordenar por adjusted_rank y seleccionar columnas en el orden exacto
    carrier_adjusted_delays = (
        carrier_summary.sort_values("adjusted_rank")[
            [
                "reporting_airline",
                "operated_flights",
                "delayed_departure_15_flights",
                "delay_rate",
                "expected_delayed_flights",
                "observed_to_expected_ratio",
                "crude_rank",
                "adjusted_rank",
            ]
        ]
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 3. Guardar CSVs sin índice y retornar las dos tablas
    # ---------------------------------------------------------
    hourly_delay_rates.to_csv(ruta_hourly, index=False)
    carrier_adjusted_delays.to_csv(ruta_carrier, index=False)

    return hourly_delay_rates, carrier_adjusted_delays
