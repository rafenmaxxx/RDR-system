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

        # Kasus instance pertama (dibandingkan dengan nothing / None)
        if cornerstone_case is None:
            for attr, val in new_case.items():
                if val is not None:
                    candidates.append(Condition(attribute=attr, operator="==", value=val))
            return candidates

        # Kasus kedua dan seterusnya (dibandingkan dengan cornerstone case yang hendak dianulir)
        for attr, new_val in new_case.items():
            if new_val is None:
                continue

            ref_val = cornerstone_case.get(attr)

            # Kondisi A: Atribut ada di new_case tetapi tidak ada di cornerstone (OWA: unknown di ref)
            if ref_val is None:
                if isinstance(new_val, bool):
                    candidates.append(Condition(attribute=attr, operator="==", value=new_val))
                elif isinstance(new_val, (int, float)):
                    # Atribut numerik baru yang tidak ada pada kasus acuan
                    candidates.append(Condition(attribute=attr, operator="==", value=new_val))
                else:
                    candidates.append(Condition(attribute=attr, operator="==", value=new_val))
                continue

            # Kondisi B: Atribut ada di kedua kasus namun nilainya berbeda
            if new_val != ref_val:
                # Penanganan khusus fitur numerikal
                if isinstance(new_val, (int, float)) and isinstance(ref_val, (int, float)):
                    if new_val > ref_val:
                        # Nilai kasus baru lebih tinggi: jadikan ambang batas bawah
                        candidates.append(Condition(attribute=attr, operator=">", value=ref_val))
                    else:
                        # Nilai kasus baru lebih rendah: jadikan ambang batas atas
                        candidates.append(Condition(attribute=attr, operator="<=", value=ref_val))
                else:
                    # Penanganan biner / boolean / kategorikal
                    candidates.append(Condition(attribute=attr, operator="==", value=new_val))

        return candidates