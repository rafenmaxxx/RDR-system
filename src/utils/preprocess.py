import pandas as pd
from pathlib import Path

# Path root proyek (RDR-system)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def preprocess_telco_churn_boolean_only(input_path: Path, output_path: Path):
    """
    Memproses dataset Telco Churn agar HANYA menggunakan kolom True/False (Boolean),
    tanpa atribut numerik (tenure, MonthlyCharges, TotalCharges dibuang).
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File mentah tidak ditemukan di: {input_path}")

    df = pd.read_csv(input_path)

    # 1. Hapus kolom ID dan seluruh atribut numerik
    drop_cols = ["customerID", "tenure", "MonthlyCharges", "TotalCharges"]
    df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    # 2. Konversi kolom biner langsung (Yes -> True, No -> False)
    binary_yes_no = ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
    for col in binary_yes_no:
        if col in df.columns:
            df[col] = df[col].map({"Yes": True, "No": False})

    # SeniorCitizen: 1 -> True, 0 -> False
    if "SeniorCitizen" in df.columns:
        df["SeniorCitizen"] = df["SeniorCitizen"].astype(bool)

    # Gender: Female -> True, Male -> False (indikator biner is_female)
    if "gender" in df.columns:
        df["is_female"] = df["gender"].map({"Female": True, "Male": False})
        df.drop(columns=["gender"], inplace=True)

    # 3. Fitur layanan tambahan: Nilai 'Yes' -> True, selain itu ('No', 'No internet/phone') -> False
    service_cols = [
        "MultipleLines", "OnlineSecurity", "OnlineBackup", 
        "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    for col in service_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: True if str(x).strip() == "Yes" else False)

    # 4. Fitur kategorikal lain: jadikan flag biner
    if "InternetService" in df.columns:
        df["has_fiber_optic"] = df["InternetService"] == "Fiber optic"
        df.drop(columns=["InternetService"], inplace=True)

    if "Contract" in df.columns:
        df["is_month_to_month"] = df["Contract"] == "Month-to-month"
        df.drop(columns=["Contract"], inplace=True)

    if "PaymentMethod" in df.columns:
        df["is_electronic_check"] = df["PaymentMethod"] == "Electronic check"
        df.drop(columns=["PaymentMethod"], inplace=True)

    # 5. Kolom target Churn (Yes / No)
    if "Churn" in df.columns:
        df["Churn"] = df["Churn"].str.strip()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Telco Churn (True-False only) berhasil diproses: {output_path}")


def preprocess_loan_approval(input_path: Path, output_path: Path):
    """
    Memproses dataset Loan Approval dengan mempertahankan fitur numerik
    untuk pemenuhan poin bonus numerikal.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File mentah tidak ditemukan di: {input_path}")

    df = pd.read_csv(input_path)

    # 1. Bersihkan spasi pada header nama kolom
    df.columns = df.columns.str.strip()

    # 2. Hapus identifier yang tidak relevan
    if "loan_id" in df.columns:
        df.drop(columns=["loan_id"], inplace=True)

    # 3. Bersihkan spasi pada nilai kategorikal
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 4. Standarisasi biner
    df["education"] = df["education"].map({"Graduate": True, "Not Graduate": False})
    df["self_employed"] = df["self_employed"].map({"Yes": True, "No": False})

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Loan dataset (Bonus Numerikal) berhasil diproses: {output_path}")


if __name__ == "__main__":
    telco_raw = RAW_DIR / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    telco_clean = PROCESSED_DIR / "telco_churn_clean.csv"

    loan_raw = RAW_DIR / "loan_approval_dataset.csv"
    loan_clean = PROCESSED_DIR / "loan_approval_clean.csv"

    preprocess_telco_churn_boolean_only(telco_raw, telco_clean)
    preprocess_loan_approval(loan_raw, loan_clean)