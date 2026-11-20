from pathlib import Path
import pandas as pd

def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        4
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "tbl0.tsv"
    
    df = pd.read_csv(ruta_archivo, sep='\t')
    
    return len(df.columns)