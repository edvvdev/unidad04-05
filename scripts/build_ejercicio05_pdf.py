"""Genera el PDF breve del Ejercicio 05 (motor recomendador reproducible)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPO_URL = os.getenv("REPO_URL", "https://github.com/edvvdev/unidad04-05")

resultados = pd.read_csv(REPORTS / "pareto_results.csv")
resumen = json.loads((REPORTS / "ejercicio05_resumen.json").read_text(encoding="utf-8"))
metricas = json.loads((REPORTS / "hybrid_metrics_alpha075.json").read_text(encoding="utf-8"))
cierre = (ROOT / "docs/CIERRE_INTERPRETATIVO_LAB09.md").read_text(encoding="utf-8")


def negritas(texto: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Title2", parent=styles["Title"], fontSize=17, spaceAfter=6))
styles.add(ParagraphStyle(name="H1s", parent=styles["Heading1"], fontSize=12.5, spaceBefore=10, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], alignment=TA_JUSTIFY, leading=13.5, fontSize=9.6))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.2, leading=10.5))

story = []
story.append(Paragraph("Ejercicio 05 · Motor recomendador reproducible", styles["Title2"]))
story.append(Paragraph(
    "INF-8239 Ciencia de Datos II (UASD) · Unidad 04 · Consolidación de LAB08 y LAB09", styles["Small"]))
story.append(Spacer(1, 6))

identificacion = [
        ["Estudiante", "Edwing Perez · matrícula: PENDIENTE"],
        ["Profesor", "Edwin Ramón José Nolasco"],
    ["Repositorio", REPO_URL],
    ["Dataset", "MovieLens Latest Small · GroupLens Research, University of Minnesota · uso académico con cita"],
    ["Fecha de ejecución", "2026-11-02"],
]
tabla_id = Table(identificacion, colWidths=[4.4 * cm, 11.4 * cm])
tabla_id.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.4),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_id)
story.append(Spacer(1, 10))

story.append(Paragraph("1. Datos, licencia, auditoría y corte temporal", styles["H1s"]))
story.append(Paragraph(
    "MovieLens <i>Latest Small</i> (100.836 valoraciones, 610 usuarios, 9.742 películas, densidad 1,70 %, "
    "periodo 2017-01-01 a 2018-09-24) se descarga por script y <b>no se redistribuye</b>: el directorio "
    "<font face='Courier'>data/raw/</font> está excluido del repositorio. Licencia y condiciones: uso "
    "académico citando la fuente (Harper y Konstan, 2015, DOI 10.1145/2827872); el conjunto es de "
    "desarrollo y puede cambiar, por lo que se registra la fecha y el SHA-256 de la descarga. "
    "Auditoría: 0 nulos, 18 duplicados de texto, clases balanceadas. La partición es un <b>corte temporal "
    "leave-one-out</b> (la última valoración de cada usuario queda como prueba), con semilla 42; una "
    "separación aleatoria dejaría que el modelo aprendiera de interacciones posteriores.", styles["BodyJ"]))
story.append(Spacer(1, 6))

story.append(Paragraph("2. Tabla principal de resultados", styles["H1s"]))
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
    ("FONTSIZE", (0, 0), (-1, -1), 8.0),
    ("ALIGN", (2, 1), (-1, -1), "CENTER"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
story.append(tabla_res)
story.append(Spacer(1, 4))
story.append(Paragraph(
    f"Híbrido principal (α=0,75, 20 factores): RMSE {metricas['rmse']:.4f} · HitRate@10 "
    f"{metricas['hit_rate_at_10']:.5f} · cobertura {metricas['catalog_coverage']:.4f} · tiempo "
    f"{metricas['train_seconds']:.2f} s · modelo {metricas['model_size_kb']:.0f} KB. "
    "Referencias: la <b>popularidad</b> acierta en el 2,13 % de los casos retenidos con 0,10 % de "
    "cobertura (10 películas para todos), y el <b>contenido</b> tiene la mayor cobertura (19,07 %) pero "
    "<b>HitRate@10 = 0</b>: recomienda lo más parecido, nunca lo retenido.", styles["Small"]))
story.append(Spacer(1, 8))

story.append(Paragraph("3. Figuras", styles["H1s"]))
story.append(Paragraph("Figura 1. Top-10 de popularidad (baseline).", styles["Small"]))
story.append(Image(str(REPORTS / "popular_top10.png"), width=14 * cm, height=7.8 * cm))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Figura 2. Utilidad frente a costo de ajuste y frente a cobertura del catálogo.", styles["Small"]))
story.append(Image(str(REPORTS / "pareto_ejercicio05.png"), width=14.5 * cm, height=5.6 * cm))
story.append(Spacer(1, 4))

story.append(PageBreak())
story.append(Paragraph("4. Conclusión y decisión", styles["H1s"]))
cuerpo = cierre.split("## Resultado de ranking", 1)[-1]
for parrafo in cuerpo.strip().split("\n\n"):
    texto = negritas(parrafo.strip().replace("\n", " "))
    if texto:
        story.append(Paragraph(texto, styles["BodyJ"]))
        story.append(Spacer(1, 4))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Uso responsable de IA.</b> El asistente de IA apoyó la redacción de las tarjetas, la "
    "extracción de la lógica del híbrido a <font face='Courier'>src/inf8239_u03/hybrid.py</font> (verificada "
    "con métricas idénticas a las del script base) y la corrección de un error de compatibilidad con "
    "NumPy 2. El estudiante conserva la responsabilidad sobre los datos, el código, las referencias y "
    "estas conclusiones; los detalles están en <font face='Courier'>AI_USE_DECLARATION.md</font>. "
    "Los errores del catálogo no son preferencias: las señales miden coincidencias de categorías y patrones de "
    "interacción, nunca garantizan que algo le gustará a una persona.", styles["Small"]))

target = ROOT / "docs/EJERCICIO_05_PDF_BRIEF.pdf"
document = SimpleDocTemplate(str(target), pagesize=LETTER, title="Ejercicio 05 · INF-8239",
                              leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
document.build(story)
print("PDF generado:", target)
