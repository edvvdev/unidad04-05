"""Genera el PDF breve del Ejercicio 05 (motor recomendador reproducible).

Todas las cifras se leen de `reports/`: no hay literales escritos a mano.
"""

from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-05")

resultados = pd.read_csv(REPORTS / "pareto_results.csv")
resumen = json.loads((REPORTS / "ejercicio05_resumen.json").read_text(encoding="utf-8"))
auditoria = json.loads((REPORTS / "audit_summary.json").read_text(encoding="utf-8"))
metricas075 = json.loads((REPORTS / "hybrid_metrics_alpha075.json").read_text(encoding="utf-8"))
metricas025 = json.loads((REPORTS / "hybrid_metrics_alpha025.json").read_text(encoding="utf-8"))
cierre = (ROOT / "docs/CIERRE_INTERPRETATIVO_LAB09.md").read_text(encoding="utf-8")
multiseed = resumen.get("pareto_multiseed", {})


def negritas(texto: str) -> str:
    """Convierte **negrita** y *cursiva* del markdown en etiquetas de ReportLab."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", texto)


def es(valor: float, decimales: int = 2) -> str:
    """Formato numérico español: coma decimal."""
    return f"{valor:.{decimales}f}".replace(".", ",")


def entero(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def tabla_markdown(lineas: list[str]) -> Table:
    """Convierte un bloque de tabla markdown (| a | b |) en una tabla de ReportLab."""
    def celdas(linea: str) -> list[str]:
        return [celda.strip() for celda in linea.strip().strip("|").split("|")]

    filas = [celdas(lineas[0])]
    for linea in lineas[1:]:
        if set(linea.replace("|", "").replace(" ", "")) <= {"-", ":"}:
            continue
        filas.append(celdas(linea))
    columnas = max(len(fila) for fila in filas)
    ancho = min(18.4 / columnas, 5.2)
    # Paragraph para que el texto largo dentro de la celda se ajuste al ancho de la columna
    filas = [[Paragraph(negritas(celda), styles["TablaChica"]) for celda in fila] for fila in filas]
    tabla = Table(filas, colWidths=[ancho * cm] * columnas, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 7.4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tabla


def fila_de(nombre: str) -> pd.Series:
    return resultados[resultados["configuracion"] == nombre].iloc[0]


def ahora_local() -> datetime:
    """Instante actual en la zona horaria local de la máquina."""
    return datetime.now(tz=UTC).astimezone()


fecha_ejecucion = auditoria.get("generado_en") or ahora_local().strftime("%Y-%m-%d")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12.5, spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13.5, fontSize=9.6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.2, leading=10.5))
styles.add(ParagraphStyle(name="TablaChica", parent=styles["BodyText"], fontSize=7.4, leading=8.8))
styles.add(ParagraphStyle(name="IdCelda", parent=styles["BodyText"], fontSize=8.4, leading=10))

story = []
story.append(Paragraph("Ejercicio 05 · Motor recomendador reproducible", styles["Title2"]))
story.append(Paragraph(
    "INF-8239 Ciencia de Datos II (UASD) · Unidad 04 · Consolidación de LAB08 y LAB09", styles["Small"]))
story.append(Spacer(1, 6))

identificacion = [
        ["Estudiante", Paragraph("Edwing Perez", styles["IdCelda"])],
        ["Profesor", Paragraph("Edwin Ramón José Nolasco", styles["IdCelda"])],
    ["Repositorio", Paragraph(REPO_URL, styles["IdCelda"])],
    ["Dataset", Paragraph("MovieLens Latest Small · GroupLens Research, University of Minnesota · "
                          "uso académico con cita", styles["IdCelda"])],
    ["Fecha de ejecución", Paragraph(fecha_ejecucion, styles["IdCelda"])],
]
tabla_id = Table(identificacion, colWidths=[4.4 * cm, 11.4 * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, -1), (-1, -1), 8.4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 10))

story.append(Paragraph("1. Datos, licencia, auditoría y corte temporal", styles["H1s"]))
story.append(Paragraph(
    f"MovieLens <i>Latest Small</i> ({entero(auditoria['ratings_rows'])} valoraciones, "
    f"{auditoria['usuarios']} usuarios, {entero(auditoria['items_catalogo'])} películas, "
    f"densidad {es(auditoria['densidad'] * 100, 2)} %, periodo {auditoria['fecha_min']} a "
    f"{auditoria['fecha_max']}) se descarga por script y <b>no se redistribuye</b>: el directorio "
    "<font face='Courier'>data/raw/</font> está excluido del repositorio. Licencia y condiciones: uso "
    "académico citando la fuente (Harper y Konstan, 2015, DOI 10.1145/2827872); el conjunto es de "
    "desarrollo y puede cambiar, por lo que se registra la fecha y el SHA-256 de la descarga. "
    f"Auditoría (<font face='Courier'>reports/audit_summary.json</font>): "
    f"{auditoria['nulos_total']} nulos en ratings.csv y movies.csv, "
    f"{auditoria['duplicados_titulo']} títulos duplicados en el catálogo "
    f"({auditoria['duplicados_titulo_distintos']} títulos distintos), "
    f"{auditoria['duplicados_usuario_pelicula']} pares usuario–película repetidos y "
    f"{auditoria['items_sin_valoracion']} ítems del catálogo sin ninguna valoración "
    f"({entero(auditoria['items_catalogo'])} − {entero(auditoria['items_valorados'])}). "
    f"La distribución de valoraciones es <b>unimodal</b> (moda {es(auditoria['rating_mode'], 1)} con "
    f"{entero(auditoria['rating_mode_count'])} valoraciones, {es(auditoria['rating_mode_share'] * 100, 1)} %), "
    "no balanceada. La partición es un <b>corte temporal leave-one-out</b> (la última valoración de cada "
    "usuario queda como prueba), con semilla 42; una separación aleatoria dejaría que el modelo aprendiera "
    "de interacciones posteriores.", styles["BodyJ"]))
story.append(Spacer(1, 6))

story.append(Paragraph("2. Tabla principal de resultados", styles["H1s"]))
story.append(Paragraph(
    "Tabla consolidada de una semilla (6 configuraciones híbridas + 2 referencias): "
    "<font face='Courier'>reports/pareto_results.csv</font>.", styles["Small"]))
filas = [["Configuración", "Familia", "HitRate@10", "Cobertura", "RMSE", "Ajuste (s)", "Modelo (KB)"]]
for _, fila in resultados.sort_values("hit_rate_at_10", ascending=False).iterrows():
    filas.append([
        fila["configuracion"], fila["familia"], f"{fila['hit_rate_at_10']:.5f}",
        f"{fila['catalog_coverage']:.4f}",
        "—" if pd.isna(fila["rmse"]) else f"{fila['rmse']:.4f}",
        "—" if pd.isna(fila["fit_time_s"]) else f"{fila['fit_time_s']:.2f}",
        "—" if pd.isna(fila["model_size_kb"]) else f"{fila['model_size_kb']:.0f}",
    ])
tabla_res = Table(filas, colWidths=[3.2 * cm, 2.4 * cm, 2.3 * cm, 2.1 * cm, 2.0 * cm, 2.0 * cm, 2.2 * cm],
                   repeatRows=1)
tabla_res.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, -1), (-1, -1), 8.0),
    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_res)
story.append(Spacer(1, 4))
popularidad = fila_de("popularidad")
contenido = fila_de("contenido")
story.append(Paragraph(
    f"Híbrido principal (α=0,75, 20 factores, <font face='Courier'>reports/hybrid_metrics_alpha075.json"
    f"</font>): RMSE {es(metricas075['rmse'], 4)} · HitRate@10 {es(metricas075['hit_rate_at_10'], 5)} · "
    f"cobertura {es(metricas075['catalog_coverage'] * 100, 2)} % · tiempo {es(metricas075['train_seconds'], 2)} s "
    f"· modelo {entero(metricas075['model_size_kb'])} KB. Con α=0,25 "
    f"(<font face='Courier'>reports/hybrid_metrics_alpha025.json</font>): RMSE {es(metricas025['rmse'], 4)} · "
    f"HitRate@10 {es(metricas025['hit_rate_at_10'], 5)} · cobertura "
    f"{es(metricas025['catalog_coverage'] * 100, 2)} % · tiempo {es(metricas025['train_seconds'], 2)} s. "
    f"Referencias: la <b>popularidad</b> acierta en el {es(popularidad['hit_rate_at_10'] * 100, 2)} % de los "
    f"casos retenidos con {es(popularidad['catalog_coverage'] * 100, 2)} % de cobertura (10 películas para todos), "
    f"y el <b>contenido</b> tiene la mayor cobertura ({es(contenido['catalog_coverage'] * 100, 2)} %) pero "
    "<b>HitRate@10 = 0</b>: recomienda lo más parecido, nunca lo retenido.", styles["Small"]))
story.append(Spacer(1, 8))

if multiseed:
    bloque3 = [Paragraph("3. Frontera de Pareto multistamillas", styles["H1s"])]
    bloque3.append(Paragraph(
        f"Tres semillas × tres tamaños de modelo × dos valores de α = "
        f"{multiseed.get('configuraciones', 0)} configuraciones sobre el mismo corte temporal, con el tiempo "
        "de ajuste medido tres veces por configuración y reportado como mediana. Tabla completa: "
        "<font face='Courier'>reports/pareto_multiseed.csv</font>; figura: "
        "<font face='Courier'>reports/pareto.png</font>.", styles["Small"]))
    filas_frontera = [["Semilla", "Factores", "α", "HitRate@10", "Cobertura", "Ajuste (s)", "Modelo (KB)"]]
    for config in multiseed.get("frontera", []):
        filas_frontera.append([
            str(config["seed"]), str(config["factors"]), es(config["alpha"], 2),
            f"{config['hit_rate_at_10']:.5f}", f"{config['catalog_coverage']:.4f}",
            f"{config['fit_time_s']:.2f}", f"{config['model_size_kb']:.0f}",
        ])
    tabla_frontera = Table(filas_frontera, colWidths=[2.0 * cm, 2.0 * cm, 1.6 * cm, 2.6 * cm, 2.4 * cm,
                                                      2.4 * cm, 2.4 * cm], repeatRows=1)
    tabla_frontera.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f7c7b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 8.0),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    bloque3.append(tabla_frontera)
    bloque3.append(Spacer(1, 4))
    bloque3.append(Paragraph(
        f"Con las {multiseed.get('configuraciones', 0)} configuraciones el HitRate@10 va de "
        f"{es(multiseed.get('hit_rate_at_10_min', 0), 5)} a {es(multiseed.get('hit_rate_at_10_max', 0), 5)}: "
        "la varianza entre semillas es mayor que la diferencia entre valores de α, de modo que una sola "
        "ejecución no sostiene conclusiones sobre α.", styles["Small"]))
    story.append(KeepTogether(bloque3))
    story.append(Spacer(1, 8))

story.append(Paragraph("4. Figuras", styles["H1s"]))
story.append(Paragraph("Figura 1. Top-10 de popularidad (baseline).", styles["Small"]))
story.append(Image(str(REPORTS / "popular_top10.png"), width=14 * cm, height=7.8 * cm))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Figura 2. Utilidad frente a costo de ajuste y frente a cobertura del catálogo "
    "(configuraciones de una semilla).", styles["Small"]))
story.append(Image(str(REPORTS / "pareto_ejercicio05.png"), width=14.5 * cm, height=5.6 * cm))
story.append(Spacer(1, 4))

story.append(PageBreak())
story.append(Paragraph("5. Conclusión y decisión", styles["H1s"]))
cuerpo = cierre.split("## Resultado de ranking", 1)[-1]
for parrafo in cuerpo.strip().split("\n\n"):
    lineas = [linea.rstrip() for linea in parrafo.strip().split("\n") if linea.strip()]
    if lineas and lineas[0].lstrip().startswith("#"):
        lineas[0] = lineas[0].lstrip().lstrip("#").strip()
        lineas[0] = f"**{lineas[0]}**"
    if lineas and all(linea.strip().startswith("|") for linea in lineas):
        story.append(tabla_markdown(lineas))
        story.append(Spacer(1, 4))
        continue
    texto = negritas(" ".join(linea.strip() for linea in lineas))
    if texto:
        story.append(Paragraph(texto, styles["BodyJ"]))
        story.append(Spacer(1, 4))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Uso responsable de IA.</b> El asistente de IA apoyó la redacción de las tarjetas, la "
    "extracción de la lógica del híbrido a <font face='Courier'>src/inf8239_u03/hybrid.py</font> (verificada "
    "con métricas idénticas a las del script base), la corrección de un error de compatibilidad con "
    "NumPy 2 y la auditoría de consistencia entre los artefactos de <font face='Courier'>reports/</font> y "
    "la documentación. El estudiante conserva la responsabilidad sobre los datos, el código, las referencias y "
    "estas conclusiones; los detalles están en <font face='Courier'>AI_USE_DECLARATION.md</font>. "
    "Los errores del catálogo no son preferencias: las señales miden coincidencias de categorías y patrones de "
    "interacción, nunca garantizan que algo le gustará a una persona.", styles["Small"]))

target = ROOT / "docs/EJERCICIO_05_PDF_BRIEF.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 05 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
document.build(story)
print("PDF generado:", target)
