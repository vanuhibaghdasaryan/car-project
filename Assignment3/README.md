# Used Car Market Dashboard

An interactive dashboard built with **Dash** and **Plotly** for exploring the Polish used car market.
Based on 200,000+ listings from `Car_sale_ads.csv`.

---

## Pages

| Page | Description |
|------|-------------|
| **Overview** | KPI cards, median price by brand, price trend by production year |
| **Market Analysis** | Fuel type comparison, body type × transmission heatmap, mileage violin plots |
| **Price Explorer** | Interactive filters (brand, fuel, year, mileage, price) with scatter + histogram |

---

## How to run

**1. Download the dataset**

The CSV file is not included in this repo due to its size. Download it from Kaggle:

 Dataset link - [Poland Cars for Sale Dataset](https://www.kaggle.com/datasets/bartoszpieniak/poland-cars-for-sale-dataset)

After downloading, rename the file to `Car_sale_ads.csv` and place it in the same folder as `app.py`.

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python app.py
```

**4. Open in browser**
```
http://127.0.0.1:8050
```

---

## Files

```
├── app.py                  # Main Dash application
├── Car_sale_ads.csv        # Dataset — download separately (see above)
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

## Dataset

Source: [Kaggle — Poland Cars for Sale](https://www.kaggle.com/datasets/bartoszpieniak/poland-cars-for-sale-dataset)

The dataset contains used car listings with fields including:
- `Vehicle_brand`, `Vehicle_model`
- `Price`, `Currency` (converted to PLN)
- `Production_year`, `Mileage_km`, `Power_HP`
- `Fuel_type`, `Transmission`, `Type` (body style)
- `Condition` (New / Used)