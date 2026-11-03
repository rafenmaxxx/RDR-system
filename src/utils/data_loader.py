import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

Case = Dict[str, Any]

class DataLoader:
    """
    Utilitas untuk membaca dataset (Kaggle/CSV/JSON) dan mengubahnya
    menjadi list kasus yang siap diproses oleh sistem RDR dengan prinsip OWA.
    """

    @staticmethod
    def _parse_value(val: str) -> Any:
        """
        Melakukan inferensi tipe data otomatis:
        - Boolean: 'true', 'false', '1', '0' (sesuai kebutuhan biner)
        - Numerik: int / float
        - None: jika string kosong (OWA: ketiadaan data bukan false)
        - String: jika nilai kategorikal
        """
        val_clean = val.strip()

        # Kasus ketiadaan nilai (OWA: jangan anggap False, melainkan None/hilang)
        if val_clean == "" or val_clean.lower() in {"na", "nan", "null", "none", "?"}:
            return None

        # Boolean parsing
        val_lower = val_clean.lower()
        if val_lower in {"true", "yes", "y", "t"}:
            return True
        if val_lower in {"false", "no", "n", "f"}:
            return False

        # Numeric parsing (Bonus)
        try:
            if "." in val_clean:
                return float(val_clean)
            return int(val_clean)
        except ValueError:
            pass

        # String kategorikal murni
        return val_clean

    @classmethod
    def load_from_csv(
        cls,
        file_path: Union[str, Path],
        target_column: Optional[str] = None
    ) -> List[Tuple[Case, Optional[str]]]:
        """
        Membaca dataset CSV dari Kaggle.
        
        Mengembalikan list tuple: (case_dict, ground_truth_label)
        Pada case_dict, nilai None otomatis difilter keluar agar memenuhi prinsip OWA:
        atribut yang tidak ada berarti 'tidak diketahui' (unknown), bukan 'False'.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File dataset tidak ditemukan di: {path}")

        records: List[Tuple[Case, Optional[str]]] = []

        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                case_data: Case = {}
                ground_truth = None

                for col, raw_val in row.items():
                    parsed_val = cls._parse_value(raw_val)

                    if target_column and col == target_column:
                        ground_truth = str(parsed_val) if parsed_val is not None else None
                    else:
                        # OWA: Hanya sertakan atribut yang ada nilainya
                        # Atribut yang kosong/None tidak dimasukkan ke dalam dictionary kasus
                        if parsed_val is not None:
                            case_data[col] = parsed_val

                records.append((case_data, ground_truth))

        return records

    @classmethod
    def load_from_json(
        cls,
        file_path: Union[str, Path],
        target_field: Optional[str] = None
    ) -> List[Tuple[Case, Optional[str]]]:
        """
        Membaca dataset dalam format JSON.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File JSON tidak ditemukan di: {path}")

        with open(path, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        records: List[Tuple[Case, Optional[str]]] = []
        for entry in data:
            target_val = entry.get(target_field) if target_field else None
            # Filter OWA: abaikan key dengan nilai None
            case_data = {k: v for k, v in entry.items() if k != target_field and v is not None}
            records.append((case_data, str(target_val) if target_val is not None else None))

        return records