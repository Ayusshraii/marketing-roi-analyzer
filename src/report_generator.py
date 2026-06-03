"""
report_generator.py
===================
Auto-generates a formatted Excel summary report combining:
- Campaign KPI summary sheet
- Creative performance ranking sheet
- A/B test results sheet

Usage:
    python src/report_generator.py
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from datetime import datetime

SUMMARY_PATH    = "data/processed/creative_summary.csv"
AB_RESULTS_PATH = "data/processed/ab_test_results.csv"
OUTPUT_XLSX     = "outputs/campaign_report.xlsx"


# ── Styling helpers ───────────────────────────────────────────
HEADER_FILL  = PatternFill("solid", fgColor="1F3864")
ACCENT_FILL  = PatternFill("solid", fgColor="2E75B6")
ALT_FILL     = PatternFill("solid", fgColor="D6E4F0")
GREEN_FILL   = PatternFill("solid", fgColor="E2EFDA")
RED_FILL     = PatternFill("solid", fgColor="FFDDC1")

HEADER_FONT  = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
TITLE_FONT   = Font(name="Calibri", bold=True, size=14, color="1F3864")
BODY_FONT    = Font(name="Calibri", size=10)

CENTER       = Alignment(horizontal="center", vertical="center")
LEFT         = Alignment(horizontal="left",   vertical="center")

THIN_BORDER  = Border(
    left=Side(style="thin"),  right=Side(style="thin"),
    top=Side(style="thin"),   bottom=Side(style="thin"),
)


def style_header_row(ws, row_num: int, num_cols: int):
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row_num, column=col)
        cell.fill      = HEADER_FILL
        cell.font      = HEADER_FONT
        cell.alignment = CENTER
        cell.border    = THIN_BORDER


def write_df_to_sheet(ws, df: pd.DataFrame, start_row=3, title=""):
    if title:
        ws.cell(row=1, column=1, value=title).font = TITLE_FONT
        ws.cell(row=2, column=1, value=f"Generated: {datetime.now().strftime('%d %b %Y')}"
                ).font = Font(name="Calibri", size=9, color="808080")

    # Header
    for col_i, col_name in enumerate(df.columns, 1):
        ws.cell(row=start_row, column=col_i, value=col_name)
    style_header_row(ws, start_row, len(df.columns))

    # Data rows
    for row_i, (_, row) in enumerate(df.iterrows(), start=start_row + 1):
        fill = ALT_FILL if row_i % 2 == 0 else None
        for col_i, val in enumerate(row, 1):
            cell = ws.cell(row=row_i, column=col_i, value=val)
            cell.font      = BODY_FONT
            cell.alignment = CENTER
            cell.border    = THIN_BORDER
            if fill:
                cell.fill = fill

    # Auto-fit columns
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 40)


def build_report():
    os.makedirs("outputs", exist_ok=True)
    wb = openpyxl.Workbook()

    # ── Sheet 1: Campaign KPI Summary ────────────────────────
    df_summary = pd.read_csv(SUMMARY_PATH)

    kpi_cols = ["campaign_id", "variant", "headline", "impressions",
                "clicks", "conversions", "spend", "revenue", "ctr_pct", "roas", "conv_rate_pct"]
    df_kpi = df_summary[kpi_cols].copy()
    df_kpi = df_kpi.sort_values("roas", ascending=False)

    ws1 = wb.active
    ws1.title = "Creative KPI Summary"
    write_df_to_sheet(ws1, df_kpi, title="📊 Creative Performance — KPI Summary")

    # Highlight top/bottom ROAS
    roas_col = kpi_cols.index("roas") + 1
    max_roas  = df_kpi["roas"].max()
    min_roas  = df_kpi["roas"].min()
    for row in ws1.iter_rows(min_row=4, max_row=ws1.max_row, min_col=roas_col, max_col=roas_col):
        for cell in row:
            if cell.value == max_roas:
                cell.fill = GREEN_FILL
            elif cell.value == min_roas:
                cell.fill = RED_FILL

    # ── Sheet 2: A/B Test Results ─────────────────────────────
    if os.path.exists(AB_RESULTS_PATH):
        df_ab = pd.read_csv(AB_RESULTS_PATH)
        ws2 = wb.create_sheet("AB Test Results")
        write_df_to_sheet(ws2, df_ab, title="🧪 A/B Test Significance Analysis")

        # Color significant rows green
        sig_col = list(df_ab.columns).index("significant") + 1
        for row in ws2.iter_rows(min_row=4, max_row=ws2.max_row):
            sig_cell = row[sig_col - 1]
            if sig_cell.value is True:
                for cell in row:
                    cell.fill = GREEN_FILL

    # ── Sheet 3: Platform Summary ─────────────────────────────
    df_plat = df_summary.groupby("campaign_id", as_index=False).agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue", "sum"),
        total_clicks=("clicks", "sum"),
        total_conversions=("conversions", "sum"),
    )
    df_plat["overall_roas"] = (df_plat["total_revenue"] / df_plat["total_spend"]).round(2)
    df_plat = df_plat.sort_values("overall_roas", ascending=False)

    ws3 = wb.create_sheet("Campaign Rollup")
    write_df_to_sheet(ws3, df_plat, title="📈 Campaign-Level Rollup")

    wb.save(OUTPUT_XLSX)
    print(f"✅ Excel report saved → {OUTPUT_XLSX}")


if __name__ == "__main__":
    build_report()
