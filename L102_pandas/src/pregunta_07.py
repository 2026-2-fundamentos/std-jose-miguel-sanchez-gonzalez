from pathlib import Path
import pandas as pd

def pregunta_07():
    """
    Usando `data/tbl0.tsv`, sume los valores de la columna `c2` para cada
    categoría de la columna `c1`. Retorne una Serie de Pandas cuyo índice son
    las categorías, en orden alfabético, y cuyos valores son las sumas.

    Ejemplo del formato de la respuesta:

        c1
        A    37
        B    36
        C    27
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "tbl0.tsv"
    
    df = pd.read_csv(ruta_archivo, sep='\t')
    
    return df.groupby('c1')['c2'].sum().sort_index()
