---
name: Training data pipeline
description: How real survey data flows from CSV upload to model retraining, including incremental learning and bias detection.
---

## Incremental Learning (TrainingBatch pool)
- Each upload is saved as a `TrainingBatch` Django model row (JSON list of rows)
- On retrain, ALL batches from the pool are combined, then blended with synthetic data
- This means future data uploads are additive — batch 2 never erases batch 1
- Initial batch: 60 real responses seeded via `manage.py shell` from Untitled form.csv

## Bias Detection
- After training, `check_bias()` in `train_model.py` checks accuracy per gender and per level
- Flags any subgroup more than 10pp below overall accuracy
- Results saved to `fastapi_ml/ml/bias_report.json`
- Accessible via FastAPI GET /bias-report and shown on the Train Model page after retraining

## CSV Value Mapping Quirks
- Google Form exports use unicode en-dash (–, U+2013) in ranges like "16 – 19", "Always (90–100%)"
- "₦" is the naira sign (U+20A6); some browsers/exports render it as "N"
- "Very involved — they follow up regularly" uses em-dash (—, U+2014)
- "600 Level" is not in categories; mapped to "500" as closest proxy
- "Less than 30 minutes away" / "30 minutes – 1 hour away" need the "away" suffix stripped
- Financial situation question (col 21) is an extra column not in the 26 model features — skipped

## train_with_real_data() signature
Returns: (accuracy: float, total_rows: int, bias_report: dict)
**Why:** The router needs all three to build the TrainResponse with bias_report field.
