from pathlib import Path
import pandas as pd

def pregunta_07():
    """
    Para cada valor distinto de la segunda columna (`value`), construya la
    lista de letras de la primera columna (`letter`) que aparecen con ese
    valor. Conserve las letras repetidas y el orden en que aparecen en el
    archivo. Retorne una lista de tuplas `(valor, letras)` ordenada por el
    valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["E", "B", "E"]), (2, ["A", "E"]), ...]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    grouped = df.groupby(1)[0].apply(list).reset_index()
    respuesta = [(row[1], row[0]) for _, row in grouped.iterrows()]
    
    return respuesta