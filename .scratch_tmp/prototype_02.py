import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import time

RNG = 42
t0 = time.time()

pm = pd.read_csv("data/processed/phone_models_clean.csv")
print("phone_models:", pm.shape)

NUM_FEATS = ["storage", "ram", "Weight", "Display_Size", "BATTERY",
             "PPI_Density", "release_year", "is_foldable"]

# ---- feature matrix -------------------------------------------------------
df = pm.copy()
df["is_foldable"] = df["is_foldable"].astype(int)
df = df.dropna(subset=NUM_FEATS + ["price_usd"]).reset_index(drop=True)
X = pd.get_dummies(df[NUM_FEATS + ["brand"]], columns=["brand"], dtype=float)
y = df["price_usd"]
print("regression rows:", X.shape, "foldables:", df.is_foldable.sum())

# ---- 5-fold CV, same folds for both models --------------------------------
kf = KFold(n_splits=5, shuffle=True, random_state=RNG)
rows = []
for name, model in [("linear_regression", LinearRegression()),
                    ("random_forest", RandomForestRegressor(
                        n_estimators=300, random_state=RNG, n_jobs=-1))]:
    fold_mse, fold_mae, fold_r2 = [], [], []
    for tr, te in kf.split(X):
        Xtr, Xte = X.iloc[tr], X.iloc[te]
        scaler = StandardScaler()
        Xtr_s = Xtr.copy(); Xte_s = Xte.copy()
        Xtr_s[NUM_FEATS] = scaler.fit_transform(Xtr[NUM_FEATS])
        Xte_s[NUM_FEATS] = scaler.transform(Xte[NUM_FEATS])
        m = model
        m.fit(Xtr_s, y.iloc[tr])
        p = m.predict(Xte_s)
        fold_mse.append(np.mean((y.iloc[te] - p) ** 2))
        fold_mae.append(np.mean(np.abs(y.iloc[te] - p)))
        fold_r2.append(m.score(Xte_s, y.iloc[te]))
    rows.append(dict(model=name, mse_mean=np.mean(fold_mse), mse_std=np.std(fold_mse),
                     mae_mean=np.mean(fold_mae), mae_std=np.std(fold_mae),
                     r2_mean=np.mean(fold_r2), r2_std=np.std(fold_r2)))
cv = pd.DataFrame(rows)
print(cv.to_string())

# ---- permutation importance on a holdout ----------------------------------
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=RNG)
sc = StandardScaler()
Xtr_s = Xtr.copy(); Xte_s = Xte.copy()
Xtr_s[NUM_FEATS] = sc.fit_transform(Xtr[NUM_FEATS])
Xte_s[NUM_FEATS] = sc.transform(Xte[NUM_FEATS])
rf = RandomForestRegressor(n_estimators=300, random_state=RNG, n_jobs=-1).fit(Xtr_s, ytr)
print("holdout R2:", rf.score(Xte_s, yte))
pi = permutation_importance(rf, Xte_s, yte, n_repeats=20, random_state=RNG, n_jobs=-1)
imp = pd.DataFrame({"feature": X.columns, "importance": pi.importances_mean}
                   ).sort_values("importance", ascending=False)
print(imp.head(10).to_string())

# ---- hypothetical Nothing foldable -----------------------------------------
CHALLENGER_BRANDS = ["Nothing", "oneplus", "google", "motorola", "oppo",
                     "xiaomi", "honor", "asus", "zte", "realme"]
spec = {c: 0.0 for c in X.columns}
spec.update({"storage": 512, "ram": 16, "Weight": 210.0, "Display_Size": 6.9,
             "BATTERY": 4300.0, "PPI_Density": 420.0, "release_year": 2027,
             "is_foldable": 1.0})
brand_cols = [c for c in X.columns if c.startswith("brand_")]
mask = df["brand"].isin([b for b in CHALLENGER_BRANDS])
challenger_mean = X.loc[mask, brand_cols].mean()
for c in brand_cols:
    spec[c] = float(challenger_mean[c])
spec_row = pd.DataFrame([spec])[X.columns]

# scale numeric with the FULL-data scaler used for prediction
sc_full = StandardScaler().fit(X[NUM_FEATS])
spec_s = spec_row.copy()
spec_s[NUM_FEATS] = sc_full.transform(spec_row[NUM_FEATS])
rf_full = RandomForestRegressor(n_estimators=300, random_state=RNG, n_jobs=-1).fit(
    pd.concat([X[NUM_FEATS].pipe(lambda d: (d - sc_full.mean_) / sc_full.scale_), X.drop(columns=NUM_FEATS)], axis=1), y)

def scale_df(d):
    d2 = d.copy()
    d2[NUM_FEATS] = sc_full.transform(d[NUM_FEATS])
    return d2

point = rf_full.predict(scale_df(spec_row))[0]
# per-tree spread
tree_preds = np.array([tree.predict(scale_df(spec_row).values)[0] for tree in rf_full.estimators_])
print("point:", point, "tree std:", tree_preds.std())

# bootstrap CI (100 resamples)
rng = np.random.default_rng(RNG)
boot = []
Xs_all = scale_df(X)
for b in range(100):
    idx = rng.integers(0, len(Xs_all), len(Xs_all))
    m = RandomForestRegressor(n_estimators=100, random_state=RNG, n_jobs=-1)
    m.fit(Xs_all.iloc[idx], y.iloc[idx])
    boot.append(m.predict(scale_df(spec_row))[0])
boot = np.array(boot)
print("CI:", np.percentile(boot, 5), np.percentile(boot, 95))
print("elapsed:", time.time() - t0)

# ---- segmentation ----------------------------------------------------------
si = pd.read_csv("data/processed/sales_india_clean.csv")
seg = si.dropna(subset=["rating", "selling_price_inr"]).copy()
brand_med = seg.groupby("brand")["selling_price_inr"].median()
tier = pd.qcut(brand_med, 3, labels=[0, 1, 2])
seg["brand_tier"] = seg["brand"].map(tier).fillna(1.0)
SEG_FEATS = ["selling_price_inr", "rating", "discount_pct", "brand_tier"]
Z = StandardScaler().fit_transform(seg[SEG_FEATS])
for k in [3, 4, 5]:
    km = KMeans(n_clusters=k, random_state=RNG, n_init=10).fit(Z)
    print(k, "inertia", km.inertia_, "sil", silhouette_score(Z, km.labels_))
km = KMeans(n_clusters=4, random_state=RNG, n_init=10).fit(Z)
seg["cluster"] = km.labels_
prof = seg.groupby("cluster").agg(
    n=("model", "size"), mean_price_inr=("selling_price_inr", "mean"),
    mean_rating=("rating", "mean"), mean_discount_pct=("discount_pct", "mean"),
    foldables=("is_foldable", "sum"))
print(prof.to_string())
print("foldable clusters:", seg[seg.is_foldable]["cluster"].value_counts().to_dict())
print("elapsed:", time.time() - t0)
