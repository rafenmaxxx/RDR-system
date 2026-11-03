from typing import Any, Dict, List, Optional
from .condition import Condition, Case

class RDRNode:
    """
    Node dalam pohon biner RDR:
    - true_child  : Anak Kanan (Dieksekusi jika kondisi node ini terpenuhi / Exception)
    - false_child : Anak Kiri  (Dieksekusi jika kondisi node ini TIDAK terpenuhi / Alternatif)
    """

    def __init__(
        self,
        node_id: int,
        conditions: List[Condition],
        conclusion: str,
        cornerstone_case: Optional[Case] = None
    ):
        self.node_id = node_id
        # Daftar kondisi konjungtif (AND). Jika kosong (misal pada Root), bernilai selalu True.
        self.conditions = conditions
        self.conclusion = conclusion
        # Kasus kunci yang memicu dibuatnya rule ini
        self.cornerstone_case = cornerstone_case
        
        # Pointer relasi pohon
        self.true_child: Optional['RDRNode'] = None   # Anak Kanan
        self.false_child: Optional['RDRNode'] = None  # Anak Kiri

    def evaluate(self, case: Case) -> bool:
        """
        Evaluasi apakah seluruh kondisi pada node ini terpenuhi oleh kasus konsumen (AND logic).
        Jika node tidak memiliki kondisi (seperti root), default bernilai True.
        """
        if not self.conditions:
            return True
        return all(cond.evaluate(case) for cond in self.conditions)

    def is_leaf(self) -> bool:
        return self.true_child is None and self.false_child is None

    def __repr__(self) -> str:
        cond_str = " AND ".join(str(c) for c in self.conditions) if self.conditions else "TRUE (Default)"
        return f"Node({self.node_id}: IF {cond_str} THEN '{self.conclusion}')"