import pandas as pd
import json
from pathlib import Path

def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "insurance.csv.gz"
    ruta_salida = directorio_actual.parent / "submission"
    ruta_archivo_salida = ruta_salida / "insurance_published.csv"
    ruta_reporte = ruta_salida / "privacy_report.json"
    
    df = pd.read_csv(ruta_entrada, sep=",")
    
    k = 5

    # 1. Análisis sobre los cuasi-identificadores originales (sin generalizar)
    original_qis = ["age", "sex", "bmi", "children", "region"]
    orig_sizes = df.groupby(original_qis).size()
    original_k = int(orig_sizes.min())
    original_unique_records = int((orig_sizes == 1).sum())

    # 2. Creación de las columnas generalizadas
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 29, 39, 49, 64],
        labels=["18-29", "30-39", "40-49", "50-64"],
    ).astype(str)

    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[-float("inf"), 18.5, 25.0, 30.0, float("inf")],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,
    ).astype(str)

    df["children_group"] = pd.cut(
        df["children"],
        bins=[-1, 0, 2, float("inf")],
        labels=["0", "1-2", "3+"],
    ).astype(str)

    # 3. Evaluación de ambos esquemas
    scheme_defs = {
        "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }

    schemes_report = {}
    published_dfs = {}

    for scheme_name, qis in scheme_defs.items():
        # Tamaño de clase por fila antes de suprimir
        class_sizes = df.groupby(qis)["smoker"].transform("size")
        equivalence_classes = int(df.groupby(qis).ngroups)
        k_before_suppression = int(class_sizes.min())

        # Supresión de registros en clases con tamaño < k (5)
        mask_published = class_sizes >= k
        pub_df = df[mask_published].copy()

        suppressed_records = int((~mask_published).sum())
        published_records = int(mask_published.sum())
        published_classes = int(pub_df.groupby(qis).ngroups)

        # Diversidad en el atributo sensible ('smoker') entre clases publicadas
        # Sin diversidad = todos fuman o ninguno fuma (nunique == 1)
        smoker_nunique = pub_df.groupby(qis)["smoker"].transform("nunique")
        no_diversity_mask = smoker_nunique == 1

        classes_without_smoker_diversity = int(
            pub_df[no_diversity_mask].groupby(qis).ngroups
        )
        records_without_smoker_diversity = int(no_diversity_mask.sum())

        schemes_report[scheme_name] = {
            "quasi_identifiers": qis,
            "equivalence_classes": equivalence_classes,
            "k_before_suppression": k_before_suppression,
            "suppressed_records": suppressed_records,
            "published_records": published_records,
            "published_classes": published_classes,
            "classes_without_smoker_diversity": classes_without_smoker_diversity,
            "records_without_smoker_diversity": records_without_smoker_diversity,
        }
        published_dfs[scheme_name] = pub_df

    # 4. Selección del esquema que suprime menos registros
    selected_scheme = min(
        scheme_defs.keys(),
        key=lambda s: schemes_report[s]["suppressed_records"],
    )
    selected_qis = scheme_defs[selected_scheme]
    selected_pub_df = published_dfs[selected_scheme]

    # 5. Métricas globales (original vs. publicado)
    mean_charges_original = float(df["charges"].mean())
    mean_charges_published = float(selected_pub_df["charges"].mean())

    smoker_rate_original = float((df["smoker"] == "yes").mean())
    smoker_rate_published = float((selected_pub_df["smoker"] == "yes").mean())

    # 6. Construcción del reporte y exportación de archivos
    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": schemes_report,
        "selected_scheme": selected_scheme,
        "mean_charges_original": mean_charges_original,
        "mean_charges_published": mean_charges_published,
        "smoker_rate_original": smoker_rate_original,
        "smoker_rate_published": smoker_rate_published,
    }

    with open(ruta_reporte, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    cols_to_publish = selected_qis + ["smoker", "charges"]
    selected_pub_df[cols_to_publish].to_csv(
        ruta_archivo_salida, index=False
    )

    return report
