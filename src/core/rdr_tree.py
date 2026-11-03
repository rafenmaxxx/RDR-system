from typing import Any, Dict, List, Optional, Tuple
from .condition import Condition, Case
from .node import RDRNode

class RippleDownRulesSystem:
    """
    Sistem Single-Classification RDR (SCRDR).
    Berawal dari satu rule default (t -> default_conclusion).
    """

    def __init__(self, default_conclusion: str):
        self._node_id_counter = 0
        
        # Root node: kondisi selalu terpenuhi (t), kasus kunci awal bernilai None (nothing)
        self.root = RDRNode(
            node_id=self._generate_id(),
            conditions=[],
            conclusion=default_conclusion,
            cornerstone_case=None
        )
        
        # Registry untuk melacak seluruh cornerstone cases yang ada di KB
        # Format item: (node_id, case, expected_conclusion)
        self.cornerstone_registry: List[Tuple[int, Case, str]] = []

    def _generate_id(self) -> int:
        self._node_id_counter += 1
        return self._node_id_counter

    def infer(self, case: Case) -> Dict[str, Any]:
        """
        Menelusuri tree biner:
        - Jika kondisi node terpenuhi (True): kesimpulan diperbarui, lanjut ke anak kanan.
        - Jika kondisi node tidak terpenuhi (False): kesimpulan TIDAK diperbarui, lanjut ke anak kiri.
        
        Mengembalikan kesimpulan terakhir yang bernilai True serta konteks evaluasi untuk koreksi pakar.
        """
        curr: Optional[RDRNode] = self.root
        last_satisfied_node: RDRNode = self.root
        last_evaluated_node: RDRNode = self.root
        last_eval_status: bool = True

        while curr is not None:
            last_evaluated_node = curr
            eval_result = curr.evaluate(case)

            if eval_result:
                # Kesimpulan terakhir dianulir oleh kesimpulan baru yang lebih spesifik
                last_satisfied_node = curr
                last_eval_status = True
                curr = curr.true_child  # Telusuri anak kanan (exception)
            else:
                # Kondisi gagal, jangan perbarui last_satisfied_node (mempertahankan kesimpulan valid sebelumnya)
                last_eval_status = False
                curr = curr.false_child  # Telusuri anak kiri (alternatif)

        return {
            "conclusion": last_satisfied_node.conclusion,
            "last_satisfied_node": last_satisfied_node,
            "last_evaluated_node": last_evaluated_node,
            "last_eval_status": last_eval_status
        }

    def add_rule(
        self,
        inference_context: Dict[str, Any],
        conditions: List[Condition],
        new_conclusion: str,
        new_case: Case
    ) -> RDRNode:
        """
        Menambahkan rule perkecualian baru ke pohon berdasarkan konteks inferensi terakhir.
        """
        new_node = RDRNode(
            node_id=self._generate_id(),
            conditions=conditions,
            conclusion=new_conclusion,
            cornerstone_case=new_case
        )

        last_evaluated: RDRNode = inference_context["last_evaluated_node"]
        last_status: bool = inference_context["last_eval_status"]

        if last_status:
            # Jika evaluasi terakhir bernilai True, letakkan sebagai anak kanan (exception)
            if last_evaluated.true_child is not None:
                raise ValueError(f"Node {last_evaluated.node_id} sudah memiliki anak kanan.")
            last_evaluated.true_child = new_node
        else:
            # Jika evaluasi terakhir bernilai False, letakkan sebagai anak kiri (alternatif)
            if last_evaluated.false_child is not None:
                raise ValueError(f"Node {last_evaluated.node_id} sudah memiliki anak kiri.")
            last_evaluated.false_child = new_node

        # Catat ke registry kasus kunci
        self.cornerstone_registry.append((new_node.node_id, new_case, new_conclusion))
        return new_node