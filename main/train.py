import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature

# -------------------------------------------------
# 1) MLflow ayarı: proje klasörüne yaz (mlruns/)
# -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
mlruns_path = PROJECT_ROOT / "mlruns"
mlflow.set_tracking_uri(mlruns_path.as_uri())
mlflow.set_experiment("student_regression_demo")

# -------------------------------------------------
# 2) Veri
#   Dosyayı proje köküne koy: student_scores.csv
#   (sütun adları: Hours, Scores)
# -------------------------------------------------
data = pd.read_csv(PROJECT_ROOT / "student_scores.csv")
X = data[["Hours"]].values
y = data["Scores"].values

# -------------------------------------------------
# 3) Model eğitimi + MLflow kaydı
# -------------------------------------------------
with mlflow.start_run(run_name="linear_regression_student"):
    model = LinearRegression()
    model.fit(X, y)

    m = float(model.coef_[0])
    b = float(model.intercept_)
    y_pred = model.predict(X)

    mse = mean_squared_error(y, y_pred)
    rmse = mse**0.5
    r2 = r2_score(y, y_pred)

    # ---- Parametre/özet bilgileri
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_param("n_samples", len(X))
    mlflow.log_param("feature", "Hours")

    # ---- Metrikler
    mlflow.log_metric("mse", float(mse))
    mlflow.log_metric("rmse", float(rmse))
    mlflow.log_metric("r2", float(r2))

    # ---- Modeli imza (signature) ile kaydet
    signature = infer_signature(X, y_pred)
    mlflow.sklearn.log_model(
        model,
        artifact_path="model",
        signature=signature,
        input_example=X[:5]
    )

    # ---- Grafik (artifact)
    plt.figure(figsize=(6,4))
    plt.scatter(data["Hours"], data["Scores"], s=20, label="Data")
    x_vals = np.linspace(data["Hours"].min(), data["Hours"].max(), 100)
    y_vals = m * x_vals + b
    plt.plot(x_vals, y_vals, linewidth=2, label="Linear fit")
    plt.xlabel("Hours"); plt.ylabel("Scores"); plt.title("Hours vs Scores")
    plt.legend(); plt.tight_layout()
    fig_path = PROJECT_ROOT / "fit_plot.png"
    plt.savefig(fig_path); plt.close()
    mlflow.log_artifact(str(fig_path))

    print(f"m={m:.4f}  b={b:.4f}  MSE={mse:.4f}  RMSE={rmse:.4f}  R2={r2:.4f}")

print("✓ Bitti. MLflow UI’da run, metrikler ve fit_plot.png görünecek.")
