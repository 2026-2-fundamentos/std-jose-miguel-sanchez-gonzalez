from pathlib import Path
import pandas as pd

def pregunta_06():
    """
    Usando `data/tbl1.tsv`, obtenga los valores distintos de la columna `c4`,
    conviértalos a mayúsculas y retórnelos como una lista ordenada
    alfabéticamente.

    Ejemplo del formato de la respuesta:

        ["A", "B", "C", "D", "E", "F", "G"]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "tbl1.tsv"
    
    df = pd.read_csv(ruta_archivo, sep='\t')
    unique_values = df['c4'].str.upper().unique()
    
    return sorted(unique_values)