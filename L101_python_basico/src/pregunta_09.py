from pathlib import Path
import pandas as pd

def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    df['metrics'] = df[4].str.split(',')
    respuesta = {}
    for i in df['metrics']:
        for j in i:
            metrics = j.split(':')
            if metrics[0] in respuesta:
                respuesta[metrics[0]] += 1
            else:
                respuesta[metrics[0]] = 1
    respuesta = dict(sorted(respuesta.items()))
    
    return respuesta