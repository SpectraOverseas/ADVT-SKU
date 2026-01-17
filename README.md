# SKU Wise Ad Spend Dashboard

This Streamlit dashboard visualizes the **SKU WISE AD SPEND** dataset using the highlighted columns only.

## Running locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

The repository is Streamlit Cloud-ready. Push to GitHub and select `streamlit_app.py` as the entry point.

## Data

The app loads `SKU WISE AD SPEND.xlsx` using `pandas` + `openpyxl`, reading only the columns listed in the prompt.
