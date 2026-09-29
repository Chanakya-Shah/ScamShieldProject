# Model Card: ScamShield Fraud Detection Model

## Model details
- **Type:** LightGBM gradient-boosted trees, tuned with Optuna (30 trials), with isotonic calibration.
- **Output:** a fraud probability for each payment; payments scoring ≥ 0.01 are flagged for review.
- **Author / date:** Chanakya Shah, September 2026.

## Intended use
- **For:** ranking payments so fraud investigators review the riskiest first.
- **Not for:** automatically blocking payments or making decisions without human review.

## Data
- PaySim: synthetic mobile-money transactions (~6.3M); only TRANSFER and CASH_OUT used (~2.77M), as fraud occurs only in these.
- Time-based split: train steps ≤ 322 (1.94M rows), validation 323–376 (416k), test > 376 (416k).
- The test period has ~5x the fraud rate of training, which inflates absolute test PR-AUC.

## Features
- 15 features using only information available **before** a payment completes: amount, sender's starting balance, time of day, and receiving-account history.
- Post-payment balance columns were excluded after they were shown to leak the label (a simulation artefact).

## Performance (test set)
- PR-AUC **0.994** (95% CI 0.992–0.995) vs logistic regression baseline 0.564; improvement +0.429 (paired bootstrap 95% CI +0.414 to +0.444).
- At the chosen threshold: **99.9% of fraud caught, 94.1% precision, 4,268 alerts.**
- With 100 alerts/day: 38.9% of fraud caught vs a maximum possible 39.1% (99.5% of achievable).
- Time-series cross-validation: PR-AUC 0.960 ± 0.022.
- A one-line rule ("flag if the payment empties the account") needs 186,801 alerts at 2.1% precision; the model needs ~44x fewer alerts at ~45x higher precision.
- Without balance features, PR-AUC drops to 0.449 (ablation).

## Explainability
- Every alert comes with its top 3 value-aware, plain-English reasons (SHAP).
- Most important features: amount as a share of balance (mean |SHAP| 1.749) and whether the payment empties the account (1.532), together ~78% of total feature impact; then sender balance, receiver account age, payment size and hour.
- Main weakness revealed by SHAP: large partial transfers that do not empty the account.

## Fraud typologies
- Four behaviour-based typologies found by clustering (k-means, validated against HDBSCAN, ARI 0.6): transfer to a brand-new account (67%), cash-out through a busy recently opened account (9%), cash-out through an established quiet account (23%), and rare zero-balance-account fraud (0.3%).
- The model catches both cash-out typologies 100% of the time and transfers to brand-new accounts 99.9%; all 3 missed frauds were large partial transfers.

## Fairness
- Tested with a **synthetic** age attribute linked to behaviour (PaySim has no demographics), to demonstrate proxy-discrimination checks.
- False positive rate by group: 18–34 0.086%, 35–64 0.060%, 65+ 0.033%; ratio 0.39 (below the 0.8 rule of thumb); chi-square p < 0.0001.
- Absolute rates are very small (251 false alarms across ~412k legitimate payments) and fraud-catch rates are equal across groups (~99.9–100%).
- The disparity runs against younger customers because of how the proxy interacted with zero-balance accounts, showing that proxy effects must be measured, not assumed.

## Limitations
- Synthetic data: PaySim's fraud is simple and dominated by account-draining. Real-world fraud would be harder to detect.
- Monetary savings figures are not realistic because PaySim amounts are very large.
- No label delay modelled: in reality, fraud is often confirmed weeks later.
- No drift monitoring yet: the model would need retraining as fraud patterns change.
- Some features are redundant (e.g. is_night vs hour), so the feature set could be simplified.

## Ethical considerations
- Wrongly flagged payments delay customers' legitimate payments; this harm may fall unequally on some groups, including vulnerable customers.
- Human review of every alert, clear reasons, and regular fairness checks are required, consistent with the FCA's Consumer Duty expectation of good customer outcomes.
- No real customer data was used.