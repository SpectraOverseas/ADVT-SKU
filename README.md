# SKU Wise Ad Spend Dashboard

This Streamlit dashboard visualizes the **SKU WISE AD SPEND** dataset using only the columns highlighted in the source file (A, B, DV, DX, DZ, EE, EF, EI, EK, EM, EN, EO).

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data source

The dashboard expects the Excel file `SKU WISE AD SPEND.xlsx` to live in the repository root. The application loads the data with `pandas` and `openpyxl`.
