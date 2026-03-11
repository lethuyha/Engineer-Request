import openpyxl
from pathlib import Path

CONFIG_FILE = Path("data/configuration.xlsx")


def _read_sheet(sheet_name):
    """Read column A (from row 2) of a named sheet. Returns empty list if missing."""
    if not CONFIG_FILE.exists():
        return []
    wb = openpyxl.load_workbook(CONFIG_FILE, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        wb.close()
        return []
    ws = wb[sheet_name]
    values = [str(row[0]).strip() for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]
    wb.close()
    return sorted(values)


def get_staff():
    return {
        "requesters": _read_sheet("Requesters"),
        "engineers":  _read_sheet("Engineers"),
        "types":      _read_sheet("Types"),
    }
