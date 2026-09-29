import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score


def bootstrap_ci(y, p, metric=average_precision_score, n=300, seed=0):
    """Score the model on many random resamples to get a 95% range."""
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].sum() == 0:
            continue
        scores.append(metric(y[idx], p[idx]))
    return np.mean(scores), np.percentile(scores, [2.5, 97.5])


def paired_bootstrap(y, p_a, p_b, metric=average_precision_score, n=300, seed=0):
    """Is model B really better than model A? Both scored on the SAME resamples."""
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].sum() == 0:
            continue
        diffs.append(metric(y[idx], p_b[idx]) - metric(y[idx], p_a[idx]))
    diffs = np.array(diffs)
    return diffs.mean(), np.percentile(diffs, [2.5, 97.5]), (diffs <= 0).mean()


def recall_at_daily_budget(y, p, day, budget=500):
    """Share of all fraud caught if investigators check the top `budget` alerts each day."""
    d = pd.DataFrame({"y": y, "p": p, "day": day})
    d["rank"] = d.groupby("day")["p"].rank(ascending=False, method="first")
    return d.loc[d["rank"] <= budget, "y"].sum() / d["y"].sum()


def cost_curve(y, p, amount, alert_cost=5.0, recovery_rate=0.8,
               thresholds=np.linspace(0.01, 0.99, 99)):
    """Net £ saved at every possible alert threshold."""
    rows = []
    for t in thresholds:
        alert = p >= t
        caught = alert & (y == 1)
        saved = recovery_rate * amount[caught].sum()
        cost = alert_cost * alert.sum()
        rows.append({"threshold": t, "net_saving": saved - cost,
                     "alerts": int(alert.sum()),
                     "recall": caught.sum() / y.sum(),
                     "precision": caught.sum() / max(alert.sum(), 1)})
    return pd.DataFrame(rows)