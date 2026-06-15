# AB Testing Ecommerce — Landing Page Experiment

> Inferential statistics · Two-proportion z-test · Power and sample-size design

## Business Problem

An e-commerce company built a new landing page and ran an A/B test to decide whether to ship it.
The decision the analysis informs is binary and consequential: **replace the current page or keep
it**. Shipping a worse page depresses conversion across all future traffic; keeping a better page
out forgoes revenue.

This is **inferential statistics, not prediction** — there is no model to score new users, only a
hypothesis to test on the experiment that ran. The cost of error is a wrong launch decision driven
by noise (a false positive that ships a page with no real benefit, or a false negative that
discards a genuine improvement). The analysis is judged on statistical rigor: a correct test, an
honest confidence interval, and an assessment of whether the experiment had the power to decide.

A naive comparison of raw conversion rates was rejected because the difference here is small enough
to be sampling noise; only a significance test with a confidence interval can support the decision.

## Dataset

[A/B Testing dataset](https://www.kaggle.com/datasets/zhangluyuan/ab-testing)

| Property | Value |
|----------|-------|
| Rows | 294,478 page views |
| Fields | user id, timestamp, group (control/treatment), landing page (old/new), converted |
| Clean rows | 290,583 after removing 3,893 misaligned assignments and duplicate users |

## Solution Strategy

1. **Acquisition** — pull the experiment log from Kaggle on demand; a versioned sample backs an offline run.
2. **Cleaning** — drop rows where the assigned group and the page shown disagree, and users with more than one record, so each user contributes one clean observation. This is the precondition for a valid comparison and is the most consequential step.
3. **Estimation** — conversion rate per group with a 95% confidence interval on the difference.
4. **Testing** — a two-proportion z-test against the null of equal conversion, at alpha = 0.05.
5. **Power** — observed power for the measured effect, plus a sample-size calculator for designing the next experiment.

## Top Insights & Hypotheses

- **The new page did not improve conversion.** Treatment converted at 11.88% versus 12.04% for control — a 0.16 pp *decrease*, not an increase.
- **The difference is not statistically significant** (p = 0.19); the 95% confidence interval for the difference spans zero.
- **The recommendation is to keep the current page**: there is no evidence the new design helps, and weak evidence it slightly hurts.
- **Data hygiene mattered**: 3,893 rows had a group/page mismatch that would have biased the comparison if left in.

## Model

A two-proportion z-test on cleaned, deduplicated assignments. The artifact stores the group
statistics, the test result and the design parameters so the dashboard reads one source of truth.

| Quantity | Value |
|----------|------:|
| Control conversion | 12.04% |
| Treatment conversion | 11.88% |
| Absolute difference | -0.16 pp |
| 95% CI of difference | [-0.39 pp, +0.08 pp] |
| p-value | 0.190 |
| Observed power | 25.8% |

## Business Results

The verdict is **fail to reject the null: keep the current landing page**. Shipping the new page
would risk a small conversion loss with no upside in evidence.

For the next experiment, the sample-size calculator quantifies the cost of certainty: detecting a
1 pp absolute lift from a 12% baseline at alpha = 0.05 and 80% power requires about **17,200 users
per group**. The dashboard lets a product team dial baseline, effect size, significance and power
and read the required sample size and power curve directly.

## How to Run

1. **Clone**
   ```
   git clone https://github.com/pmusachio/ab-testing-ecommerce.git
   cd ab-testing-ecommerce
   ```
2. **Environment**
   ```
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Kaggle access** — place a Kaggle API token at `~/.kaggle/`; the pipeline falls back to the versioned sample if none is present.
4. **Run the pipeline**
   ```
   python -m src.pipeline
   ```
5. **Tests**
   ```
   pytest tests/
   ```
6. **App (local)**
   ```
   streamlit run app/streamlit_app.py
   ```
7. **Live app** — [ab-testing-ecommerce.onrender.com](https://ab-testing-ecommerce.onrender.com) — read the verdict and size your next test.

## Next Steps

- Segment the effect by device and time-of-day: an average null can hide offsetting wins and losses that change the decision.
- Add a sequential / Bayesian monitoring scheme so future tests can stop early when the evidence is conclusive, instead of running to a fixed size.
- Track a guardrail metric (revenue per session) alongside conversion, since a page can lift conversion while lowering basket value.
