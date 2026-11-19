from pathlib import Path
import pandas as pd

def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    respuesta = {}
    c = 0
    for fila in df[3]:
        letras = fila.split(',')
        for j in letras:
            if j in respuesta:
                respuesta[j] += df[1][c]
            else:
                respuesta[j] = df[1][c]
        c += 1
    respuesta = dict(sorted(respuesta.items()))
    return respuesta

print(pregunta_11())