from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "solicitudes_de_credito.csv.gz"
    ruta_salida = directorio_actual.parent / "submission" / "solicitudes_de_credito.csv"
    
    df = pd.read_csv(ruta_entrada, sep=";", index_col=0)
    
    # 1. Eliminar registros incompletos (conservando los nulos de comuna_ciudadano)
    columnas_obligatorias = [
        col for col in df.columns if col != "comuna_ciudadano"
    ]
    df = df.dropna(subset=columnas_obligatorias).copy()

    # 2. Normalizar columnas de texto: minúsculas, cambiar '_' y '-' por espacios y limpiar bordes
    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]
    for col in columnas_texto:
        df[col] = (
            df[col]
            .astype(str)
            .str.lower()
            .str.replace("_", " ", regex=False)
            .str.replace("-", " ", regex=False)
            .str.strip()
        )

    # 3. Limpiar 'estrato' y 'monto_del_credito' como números enteros
    df["estrato"] = df["estrato"].astype(int)

    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
        .astype(int)
    )

    # 4. Estandarizar 'fecha_de_beneficio' al formato AAAA-MM-DD
    # El dataset mezcla formatos DD/MM/AAAA y AAAA/MM/DD
    fecha_dmy = pd.to_datetime(
        df["fecha_de_beneficio"], format="%d/%m/%Y", errors="coerce"
    )
    fecha_ymd = pd.to_datetime(
        df["fecha_de_beneficio"], format="%Y/%m/%d", errors="coerce"
    )
    df["fecha_de_beneficio"] = fecha_dmy.fillna(fecha_ymd).dt.strftime("%Y-%m-%d")

    # 5. Eliminar registros duplicados
    df = df.drop_duplicates()

    # 6. Asegurar el orden exacto de las 9 columnas y guardar
    columnas_finales = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "estrato",
        "comuna_ciudadano",
        "fecha_de_beneficio",
        "monto_del_credito",
        "línea_credito",
    ]
    df = df[columnas_finales]
    
    df.to_csv(ruta_salida, sep=";", index=False)

    return df
