from pathlib import Path
import pandas as pd

def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    df['metrics'] = df[4].str.split(',')
    min = {}
    max = {}
    for i in df['metrics']:
        for j in i:
            key, value = j.split(':')
            if key not in min or int(value) < min[key]:
                min[key] = int(value)
            if key not in max or int(value) > max[key]:
                max[key] = int(value)
    respuesta = [(key, min[key], max[key]) for key in sorted(min.keys())]
    
    return respuesta