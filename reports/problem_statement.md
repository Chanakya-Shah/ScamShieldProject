# ScamShield: Problem Statement

## 1. Business problem
Payment fraud causes financial losses for the bank and real harm to customers.
Fraud investigators can only review a limited number of payments each day,
so they need to focus on the riskiest ones first.

## 2. Goal
Build a model that gives every payment a fraud risk score, so investigators
can review the most suspicious payments first.

## 3. Why accuracy is the wrong metric
Only around 0.1% of payments are fraud. A model that says "not fraud" every
time would be 99.9% accurate but would catch zero fraud. Accuracy hides
failure on rare events, so it is not used.

## 4. Success metrics
- **PR-AUC** (precision-recall area under the curve): how well the model
  ranks fraud above normal payments.
- **Recall at a daily alert budget**: the share of all fraud caught if
  investigators review the top 500 alerts per day.
- **Net £ saved**: fraud value stopped minus the cost of reviewing alerts.

## 5. Constraints
- The model may only use information available **before** the payment completes.
- Every alert must come with human-readable reasons.
- The model must not treat customer groups unfairly.
- A human reviews every alert; the model never blocks payments on its own.

## 6. Data
PaySim: a synthetic dataset of about 6.3 million mobile-money transactions
over 30 days. Because it is synthetic, it contains no real customer data,
but results may not fully reflect real-world fraud behaviour.