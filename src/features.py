import polars as pl

# The list of clues the model is allowed to use
FEATURES = [
    "is_transfer", "log_amount", "oldbalanceOrg", "amt_to_bal", "orig_zero_bal",
    "drains_account", "is_round", "hour", "is_night",
    "dest_prior_txn", "dest_prior_amt", "dest_age_hours", "dest_is_new",
    "dest_txn_24h", "dest_amt_24h",
]


def add_features(df: pl.DataFrame) -> pl.DataFrame:
    # --- Simple clues from the payment itself ---
    df = df.sort("step").with_columns(
        hour=pl.col("step") % 24,
        day=pl.col("step") // 24,
        is_transfer=(pl.col("type") == "TRANSFER").cast(pl.Int8),
        log_amount=pl.col("amount").log1p(),
        amt_to_bal=pl.col("amount") / (pl.col("oldbalanceOrg") + 1),
        orig_zero_bal=(pl.col("oldbalanceOrg") == 0).cast(pl.Int8),
        drains_account=((pl.col("amount") >= pl.col("oldbalanceOrg")) &
                        (pl.col("oldbalanceOrg") > 0)).cast(pl.Int8),
        is_round=((pl.col("amount") % 1000) == 0).cast(pl.Int8),
    ).with_columns(
        is_night=pl.col("hour").is_between(0, 5).cast(pl.Int8),
    )

    # --- History of the RECEIVING account, using only EARLIER hours ---
    per = (df.group_by(["nameDest", "step"])
             .agg(n=pl.len(), amt=pl.col("amount").sum())
             .sort(["nameDest", "step"]))

    per = per.with_columns(
        dest_prior_txn=pl.col("n").cum_sum().over("nameDest") - pl.col("n"),
        dest_prior_amt=pl.col("amt").cum_sum().over("nameDest") - pl.col("amt"),
        dest_first_step=pl.col("step").first().over("nameDest"),
    )

    # Payments received in the previous 24 hours (not counting the current hour)
    roll = (per.rolling(index_column="step", period="24i",
                        group_by="nameDest", closed="left")
               .agg(dest_txn_24h=pl.col("n").sum(),
                    dest_amt_24h=pl.col("amt").sum()))

    per = (per.join(roll, on=["nameDest", "step"], how="left")
              .with_columns(pl.col("dest_txn_24h").fill_null(0),
                            pl.col("dest_amt_24h").fill_null(0)))

    df = df.join(
        per.select(["nameDest", "step", "dest_prior_txn", "dest_prior_amt",
                    "dest_first_step", "dest_txn_24h", "dest_amt_24h"]),
        on=["nameDest", "step"], how="left",
    ).with_columns(
        dest_age_hours=pl.col("step") - pl.col("dest_first_step"),
        dest_is_new=(pl.col("dest_prior_txn") == 0).cast(pl.Int8),
    )

    return df.sort("step")