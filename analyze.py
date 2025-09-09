#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "output")
os.makedirs(OUT_DIR, exist_ok=True)

def load_mapping():
    path = os.path.join(DATA_DIR, "formula_mapping.csv")
    mp = {}
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for _, r in df.iterrows():
                o = str(r.get("old","")).strip(); n = str(r.get("new","")).strip()
                if o and n: mp[o] = n
            if mp: print("ℹ️  Loaded mapping:", mp)
        except Exception as e:
            print("⚠️  mapping read error:", e)
    return mp

def apply_mapping(df, mp):
    if not mp: return df
    out = df.copy(); out["formula"] = out["formula"].map(lambda x: mp.get(x, x)); return out

def summarize(df, label):
    summary = (df.groupby("formula")
        .agg(n=("delta_t","count"),
             mean_delta=("delta_t","mean"),
             std_delta=("delta_t","std"),
             min_delta=("delta_t","min"),
             p25=("delta_t", lambda x: np.percentile(x,25)),
             median=("delta_t","median"),
             p75=("delta_t", lambda x: np.percentile(x,75)),
             max_delta=("delta_t","max"))
        .reset_index())
    summary.to_csv(os.path.join(OUT_DIR, f"summary_{label}.csv"), index=False)
    return summary

def ranking(summary, label):
    r = summary.copy()
    r["score"] = (0.30*r["mean_delta"].fillna(0.0) + 0.40*r["median"].fillna(0.0)
                  + 0.30*r["p75"].fillna(0.0) - 0.10*r["std_delta"].fillna(0.0)
                  + 0.02*np.sqrt(r["n"].fillna(0.0)))
    r = r.sort_values("score", ascending=False).reset_index(drop=True)
    r.to_csv(os.path.join(OUT_DIR, f"ranking_{label}.csv"), index=False); return r

def plot_timeseries(df_long, outside, fname):
    plt.figure(figsize=(10,5))
    for f, sub in df_long.sort_values("date").groupby("formula"):
        plt.plot(sub["date"], sub["inside"], label=f)
    plt.plot(outside["date"], outside["outside"], '--', linewidth=2, label="Outside")
    plt.xlabel("Date"); plt.ylabel("Temperature (°C)"); plt.title("Daily Avg: Inside vs Outside")
    plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, fname), dpi=150); plt.close()

def plot_bar(summary, fname, title):
    import numpy as np, matplotlib.pyplot as plt
    plt.figure(figsize=(8,5)); x = np.arange(len(summary))
    plt.bar(x, summary["mean_delta"]); plt.xticks(x, summary["formula"])
    plt.ylabel("Mean ΔT (°C)"); plt.title(title); plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fname), dpi=150); plt.close()

def plot_box(df_long, summary, fname):
    plt.figure(figsize=(8,5))
    data = [df_long.loc[df_long["formula"]==f, "delta_t"].values for f in summary["formula"]]
    plt.boxplot(data, labels=summary["formula"].tolist())
    plt.ylabel("ΔT (°C)"); plt.title("ΔT Distribution by Formula")
    plt.tight_layout(); plt.savefig(os.path.join(OUT_DIR, fname), dpi=150); plt.close()

def main():
    daily = pd.read_csv(os.path.join(DATA_DIR, "paint_thermal_daily_from_pdf_table11.csv"), parse_dates=["date"])
    mp = load_mapping(); daily = apply_mapping(daily, mp)
    daily_summary = summarize(daily, "daily"); daily_rank = ranking(daily_summary, "daily")
    outside = daily.groupby("date")["outside"].first().reset_index()
    plot_timeseries(daily, outside, "timeseries_daily.png")
    plot_bar(daily_summary, "mean_delta_daily.png", "Mean ΔT by Formula (Daily)")
    plot_box(daily, daily_summary, "boxplot_daily.png")

    uvc = pd.read_csv(os.path.join(DATA_DIR, "uvc_daily_from_pdf_tables12_13.csv"), parse_dates=["date"])
    uvc = apply_mapping(uvc, mp)
    uvc_summary = summarize(uvc, "uvc"); uvc_rank = ranking(uvc_summary, "uvc")
    plot_bar(uvc_summary, "mean_delta_uvc.png", "Mean ΔT by Formula (UVC)")

    print("✅ Done. See output/ for results.")
    print("\n-- Daily ranking --\n", daily_rank)
    print("\n-- UVC ranking --\n", uvc_rank)

if __name__ == "__main__":
    main()
