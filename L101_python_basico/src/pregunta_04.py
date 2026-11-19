from pathlib import Path
import pandas as pd

def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    
    partes_fecha = df[2].str.split("-", expand=True)
    df["month"] = partes_fecha[1]
    conteo = df["month"].value_counts().sort_index()
    respuesta = [(mes, cantidad) for mes, cantidad in conteo.items()]
    
    return respuesta