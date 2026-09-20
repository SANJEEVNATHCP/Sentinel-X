from pathlib import Path

import pandas as pd

from ml.data_loader import load_statement


def test_csv_and_xlsx_loading(tmp_path: Path):
    frame = pd.DataFrame({"date": ["2025-01-01", "2025-01-02"], "description": ["A", "B"], "debit": [100, 0], "credit": [0, 250], "balance": [900, 1150], "reference": ["R1", "R2"]})
    csv_path = tmp_path / "statement.csv"
    xlsx_path = tmp_path / "statement.xlsx"
    frame.to_csv(csv_path, index=False)
    frame.to_excel(xlsx_path, index=False)
    assert len(load_statement(csv_path)) == 2
    assert load_statement(xlsx_path)["amount"].tolist() == [100, 250]
