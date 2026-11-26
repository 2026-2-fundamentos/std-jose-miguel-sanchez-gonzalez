import csv
from pathlib import Path
import pandas as pd

def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    base_dir = directorio_actual.parent / "data"
    salida_dir = directorio_actual.parent / "submission"
    salida_dir.mkdir(parents=True, exist_ok=True)

    for division in ["train", "test"]:
        division_dir = base_dir / division
        registros = []

        for carpeta_sentimiento in sorted(division_dir.iterdir()):
            if not carpeta_sentimiento.is_dir():
                continue

            sentimiento = carpeta_sentimiento.name

            for archivo_txt in sorted(carpeta_sentimiento.glob("*.txt")):
                frase = archivo_txt.read_text(encoding="utf-8").strip()
                registros.append({
                    "phrase": frase,
                    "target": sentimiento,
                })

        df = pd.DataFrame(registros, columns=["phrase", "target"])
        df["phrase"] = df["phrase"].str.strip()
        df.to_csv(
            salida_dir / f"{division}_dataset.csv",
            index=False,
            quoting=csv.QUOTE_ALL,
        )

#pregunta_01()