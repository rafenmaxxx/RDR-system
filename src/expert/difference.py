from typing import Any, Dict, List, Optional
from src.core.condition import Condition, Case

class DifferenceExtractor:
    """
    Mengekstraksi atribut-atribut pembeda/signifikan antara kasus baru (new_case)
    dan kasus kunci (cornerstone_case) yang hendak dianulir.
    """

    @staticmethod
    def extract_candidates(new_case: Case, cornerstone_case: Optional[Case]) -> List[Condition]:
        """
        Menghasilkan daftar kandidat kondisi pembeda.
        
        Aturan:
        1. Jika cornerstone_case adalah None (kasus pertama / instance pertama vs nothing):
           Semua atribut yang ada pada new_case dijadikan kandidat kondisi awal.
        2. Jika ada cornerstone_case:
           - Sesuai OWA: jika suatu atribut ada di new_case tetapi TIDAK ADA di cornerstone_case,
             atribut tersebut otomatis menjadi kandidat pembeda signifikan.
           - Untuk atribut biner/kategorikal: jika nilainya berbeda, ambil nilai new_case.
           - Untuk atribut numerikal (bonus): hasilkan relasi pembeda ('>' atau '<=').
        """
        candidates: List[Condition] = []

        # 1. Kasus pertama (dibandingkan dengan None / nothing)
        if cornerstone_case is None:
            for attr, val in new_case.items():
                if val is not None:
                    if isinstance(val, bool):
                        candidates.append(Condition(attr, "==", val))
                    elif isinstance(val, (int, float)) and not isinstance(val, bool):
                        candidates.append(Condition(attr, ">=", val))
                    else:
                        candidates.append(Condition(attr, "==", val))
            return candidates

        # 2. Kasus berikutnya (dibandingkan dengan cornerstone case)
        for attr, val_new in new_case.items():
            if val_new is None:
                continue

            # Prinsip OWA: Atribut ada di kasus baru tapi tidak ada di cornerstone
            if attr not in cornerstone_case or cornerstone_case[attr] is None:
                candidates.append(Condition(attr, "==", val_new))
                continue

            val_cs = cornerstone_case[attr]

            # Jika nilainya sama persis, bukan pembeda
            if val_new == val_cs:
                continue

            # --- PERBAIKAN DI SINI ---
            # A. Tangani BOOLEAN secara eksplisit terlebih dahulu
            if isinstance(val_new, bool) or isinstance(val_cs, bool):
                candidates.append(Condition(attr, "==", val_new))

            # B. Tangani NUMERIK (khusus angka murni, bukan bool)
            elif isinstance(val_new, (int, float)) and isinstance(val_cs, (int, float)):
                if float(val_new) > float(val_cs):
                    candidates.append(Condition(attr, ">", val_cs))
                else:
                    candidates.append(Condition(attr, "<=", val_cs))

            # C. Tangani KATEGORIAL / STRING
            else:
                candidates.append(Condition(attr, "==", val_new))

        return candidates