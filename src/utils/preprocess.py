import pandas as pd
import numpy as np
from pathlib import Path

def preprocess_loan_approval(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    
    # 1. Bersihkan spasi pada header
    df.columns = df.columns.str.strip()
    
    # 2. Hapus identifier
    if "loan_id" in df.columns:
        df.drop(columns=["loan_id"], inplace=True)
        
    # 3. Bersihkan spasi nilai string
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
        
    # 4. Standarisasi biner
    df["education"] = df["education"].map({"Graduate": True, "Not Graduate": False})
    df["self_employed"] = df["self_employed"].map({"Yes": True, "No": False})
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Loan dataset berhasil diproses: {output_path}")

def preprocess_telco_churn(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    
    # 1. Hapus identifier
    if "customerID" in df.columns:
        df.drop(columns=["customerID"], inplace=True)
        
    # 2. Tangani whitespace pada TotalCharges -> OWA: missing/None
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip(), errors="coerce")
    
    # 3. Standarisasi biner
    binary_cols = ["Partner", "Dependents", "PhoneService", "PaperlessBilling"]
    for col in binary_cols:
        df[col] = df[col].map({"Yes": True, "No": False})
        
    df["SeniorCitizen"] = df["SeniorCitizen"].astype(bool)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[OK] Telco dataset berhasil diproses: {output_path}")

if __name__ == "__main__":
    preprocess_loan_approval(
        "loan_approval_dataset.csv", 
        "data/processed/loan_approval_clean.csv"
    )
    preprocess_telco_churn(
        "WA_Fn-UseC_-Telco-Customer-Churn.csv", 
        "data/processed/telco_churn_clean.csv"
    )