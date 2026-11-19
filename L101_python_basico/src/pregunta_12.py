from pathlib import Path
import pandas as pd

def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_archivo = directorio_actual.parent / "data" / "data.csv.gz"
    
    df = pd.read_csv(ruta_archivo, header=None, sep="\t")
    df[4] = df[4].str.split(",")
    respuesta = {}
    c = 0
    for lista in df[4]:
        for elemento in lista:
            clave, valor = elemento.split(":")
            if df[0][c] in respuesta:
                respuesta[df[0][c]] += int(valor)
            else:
                respuesta[df[0][c]] = int(valor)
        c += 1
    respuesta = dict(sorted(respuesta.items()))
    return respuesta