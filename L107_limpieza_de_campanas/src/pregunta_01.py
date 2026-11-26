import pandas as pd
from pathlib import Path

def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
    archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
    información mezclada del cliente, de la campaña y del contexto económico.
    Su tarea es leerlos directamente desde los archivos comprimidos, sin
    descomprimirlos a mano, y separarlos en tres tablas limpias.

    Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
    de Pandas y con las columnas en el orden indicado:

    1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
       `credit_default` y `mortgage`.
       - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
       - En `education`, cambie los puntos por guiones bajos y deje el valor
         `unknown` como faltante.
       - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
         en cualquier otro caso.

    2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
       `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
       `last_contact_date`.
       - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
         cualquier otro caso.
       - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
         cualquier otro caso.
       - Construya `last_contact_date` a partir de las columnas `month` y
         `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

    3. `economics.csv`: `client_id`, `cons_price_idx` y
       `euribor_three_months`.

    La función también debe retornar las tres tablas, en el orden `client`,
    `campaign` y `economics`.

    Ejemplo del formato de `campaign.csv`:

        client_id,number_contacts,contact_duration,...,last_contact_date
        0,1,261,...,2022-05-13
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "bank-marketing-campaing-*.csv.gz"
    ruta_salida = directorio_actual.parent / "submission"
    
    df = pd.concat(pd.read_csv(f, sep=",") for f in ruta_entrada.parent.glob(ruta_entrada.name))
    
    # ---------------------------------------------------------
    # 2. Tabla: client.csv
    # ---------------------------------------------------------
    client = df[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()

    # Eliminar puntos y cambiar guiones por guiones bajos en 'job'
    client["job"] = (
        client["job"]
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )

    # Cambiar puntos por guiones bajos y convertir 'unknown' a faltante (NA) en 'education'
    client["education"] = (
        client["education"]
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )

    # 1 si es 'yes', 0 en cualquier otro caso
    client["credit_default"] = (client["credit_default"] == "yes").astype(int)
    client["mortgage"] = (client["mortgage"] == "yes").astype(int)

    # ---------------------------------------------------------
    # 3. Tabla: campaign.csv
    # ---------------------------------------------------------
    campaign = df[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
        ]
    ].copy()

    # 1 si es 'success' / 'yes', 0 en cualquier otro caso
    campaign["previous_outcome"] = (df["previous_outcome"] == "success").astype(int)
    campaign["campaign_outcome"] = (df["campaign_outcome"] == "yes").astype(int)

    # Construir 'last_contact_date' con año 2022 y formato AAAA-MM-DD
    meses = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }
    mes_num = df["month"].str.lower().map(meses)
    dia_num = df["day"].astype(str).str.zfill(2)
    campaign["last_contact_date"] = "2022-" + mes_num + "-" + dia_num

    # ---------------------------------------------------------
    # 4. Tabla: economics.csv
    # ---------------------------------------------------------
    economics = df[
        [
            "client_id",
            "cons_price_idx",
            "euribor_three_months",
        ]
    ].copy()

    # ---------------------------------------------------------
    # 5. Guardar los CSV sin índice y retornar las tablas
    # ---------------------------------------------------------
    client.to_csv(ruta_salida / "client.csv", index=False)
    campaign.to_csv(ruta_salida / "campaign.csv", index=False)
    economics.to_csv(ruta_salida / "economics.csv", index=False)

    return client, campaign, economics