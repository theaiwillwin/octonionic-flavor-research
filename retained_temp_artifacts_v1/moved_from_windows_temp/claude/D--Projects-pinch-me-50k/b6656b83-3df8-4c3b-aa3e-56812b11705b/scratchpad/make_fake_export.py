import pandas as pd, numpy as np

df = pd.read_csv(r"D:\Projects\pinch_me_50k\data\events.csv")
export = df.drop(columns=["payday_dom", "stability_t", "engagement",
                          "card_expired", "card_quality", "label"])
base = r"C:\Users\theai\AppData\Local\Temp\claude\D--Projects-pinch-me-50k\b6656b83-3df8-4c3b-aa3e-56812b11705b\scratchpad"
export.to_csv(base + r"\fake_real_events.csv", index=False)

# fake retry-attempt webhooks: ~55% of failed charges recover on retry
rng = np.random.default_rng(3)
fails = df[df.first_outcome == "fail"]
att = pd.DataFrame(dict(charge_id=fails.charge_id.values, attempt_no=1,
                        outcome=np.where(rng.random(len(fails)) < 0.55, "success", "fail")))
att.to_csv(base + r"\fake_real_attempts.csv", index=False)
print("export cols:", list(export.columns))
print("rows:", len(export), "attempts:", len(att))
