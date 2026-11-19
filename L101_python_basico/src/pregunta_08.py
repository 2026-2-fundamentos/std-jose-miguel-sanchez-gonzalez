from pathlib import Path
import pandas as pd

def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    grouped = df.groupby(1)[0].apply(list).reset_index()
    respuesta = [(row[1], sorted(set(row[0]))) for _, row in grouped.iterrows()]
    
    return respuesta