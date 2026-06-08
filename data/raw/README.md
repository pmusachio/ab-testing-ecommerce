# Data

Kaggle source: [A/B Testing](https://www.kaggle.com/datasets/zhangluyuan/ab-testing).

Expected files in this folder:

- `ab_data.csv`

The main flow uses `ab_data.csv`, which contains the experiment group, landing page and conversion flag.

## Download via Kaggle API

```bash
mkdir -p data/raw
kaggle datasets download -d zhangluyuan/ab-testing --unzip -p data/raw
find data/raw -maxdepth 1 -name "*.zip" -exec unzip -q -o {} -d data/raw \;
```

Keep large files out of Git when possible and re-download them in Colab or in your local environment.
