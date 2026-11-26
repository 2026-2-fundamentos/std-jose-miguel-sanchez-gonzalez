import pandas as pd
from pathlib import Path

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """
    directorio_actual = Path(__file__).resolve().parent
    ruta_entrada = directorio_actual.parent / "data" / "superstore_orders.csv.gz"
    ruta_profitability = directorio_actual.parent / "submission" / "profitability_summary.csv"
    ruta_discount = directorio_actual.parent / "submission" / "discount_summary.csv"
    ruta_priority = directorio_actual.parent / "submission" / "priority_segments.csv"
    
    df = pd.read_csv(ruta_entrada, sep=";", decimal=",")
    
    # Columnas auxiliares a nivel de línea
    df["is_loss"] = df["Profit"] < 0
    df["loss_amount"] = (-df["Profit"]).clip(lower=0)

    # ---------------------------------------------------------
    # 1. Tabla: profitability_summary.csv
    # ---------------------------------------------------------
    lines = len(df)
    orders = df["Order ID"].nunique()
    sales = df["Sales"].sum()
    profit = df["Profit"].sum()
    profit_margin = profit / sales
    loss_lines = int(df["is_loss"].sum())
    loss_line_rate = loss_lines / lines
    lost_profit = df["loss_amount"].sum()

    profitability_summary = pd.DataFrame(
        [
            {
                "lines": lines,
                "orders": orders,
                "sales": sales,
                "profit": profit,
                "profit_margin": profit_margin,
                "loss_lines": loss_lines,
                "loss_line_rate": loss_line_rate,
                "lost_profit": lost_profit,
            }
        ]
    )

    # ---------------------------------------------------------
    # 2. Tabla: discount_summary.csv
    # ---------------------------------------------------------
    band_order = ["0%", "1%-5%", "6%-10%", "más de 10%"]

    df["discount_band"] = pd.cut(
        df["Discount"],
        bins=[-float("inf"), 0.0, 0.05, 0.10, float("inf")],
        labels=band_order,
        right=True,
    )

    discount_summary = (
        df.groupby("discount_band", observed=False)
        .agg(
            lines=("Order ID", "count"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            loss_lines=("is_loss", "sum"),
            lost_profit=("loss_amount", "sum"),
        )
        .reindex(band_order)
        .reset_index()
    )

    discount_summary["profit_margin"] = (
        discount_summary["profit"] / discount_summary["sales"]
    )
    discount_summary["loss_line_rate"] = (
        discount_summary["loss_lines"] / discount_summary["lines"]
    )

    discount_summary = discount_summary[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]

    # ---------------------------------------------------------
    # 3. Tabla: priority_segments.csv
    # ---------------------------------------------------------
    segments = (
        df.groupby(["Customer Segment", "Product Category"], as_index=False)
        .agg(
            lines=("Order ID", "count"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            lost_profit=("loss_amount", "sum"),
        )
    )

    segments = segments[segments["lines"] >= 100].copy()
    segments["profit_margin"] = segments["profit"] / segments["sales"]

    priority_segments = (
        segments.sort_values(by="lost_profit", ascending=False)
        .head(5)[
            [
                "Customer Segment",
                "Product Category",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "lost_profit",
            ]
        ]
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 4. Guardar CSVs sin índice y retornar las tres tablas
    # ---------------------------------------------------------
    profitability_summary.to_csv(
        ruta_profitability, index=False
    )
    discount_summary.to_csv(
        ruta_discount, index=False
    )
    priority_segments.to_csv(
        ruta_priority, index=False
    )

    return profitability_summary, discount_summary, priority_segments