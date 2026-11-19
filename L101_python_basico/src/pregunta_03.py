from pathlib import Path
import pandas as pd

def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    
    suma = df.groupby(0)[1].sum()
    respuesta = [(letra, cantidad) for letra, cantidad in suma.items()]
    
    return respuesta
