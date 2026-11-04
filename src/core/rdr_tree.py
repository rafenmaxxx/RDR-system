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

    def get_tree_text(self, node: Optional[RDRNode] = None, prefix: str = "", branch_type: Optional[str] = None) -> str:
        """
        Menghasilkan representasi pohon keputusan dalam bentuk teks berjenjang (ASCII Tree).
        """
        if node is None:
            if prefix == "" and branch_type is None:
                node = self.root
            else:
                return ""

        cond_str = " AND ".join(str(c) for c in node.conditions) if node.conditions else "True (Default)"
        
        if branch_type == "TRUE":
            branch_label = "──[TRUE / Exception]──> "
        elif branch_type == "FALSE":
            branch_label = "──[FALSE / Alternatif]─> "
        else:
            branch_label = "[ROOT] "

        lines = [f"{prefix}{branch_label}Node {node.node_id}: IF {cond_str} THEN '{node.conclusion}'"]

        child_prefix = prefix + ("    " if branch_type is not None else "")
        if node.true_child:
            lines.append(self.get_tree_text(node.true_child, child_prefix + "│   ", "TRUE"))
        if node.false_child:
            lines.append(self.get_tree_text(node.false_child, child_prefix + "    ", "FALSE"))

        return "\n".join(lines)

    def export_graphviz_dot(self) -> str:
        """
        Mengekspor struktur pohon ke format Graphviz (DOT) agar dapat dirender menjadi gambar diagram.
        """
        lines = [
            "digraph RDRTree {",
            '  node [shape=box, style="rounded,filled", fillcolor="#E8F0FE", fontname="Helvetica"];',
            '  edge [fontname="Helvetica", fontsize=10];'
        ]

        def traverse(curr: Optional[RDRNode]):
            if curr is None:
                return
            cond_str = "\\nAND ".join(str(c) for c in curr.conditions) if curr.conditions else "True (Root)"
            label = f"Node {curr.node_id}\\nIF {cond_str}\\nTHEN '{curr.conclusion}'"
            lines.append(f'  node_{curr.node_id} [label="{label}"];')

            if curr.true_child:
                lines.append(
                    f'  node_{curr.node_id} -> node_{curr.true_child.node_id} '
                    f'[label="True (Exception)", color="#2E7D32", fontcolor="#2E7D32", penwidth=1.5];'
                )
                traverse(curr.true_child)

            if curr.false_child:
                lines.append(
                    f'  node_{curr.node_id} -> node_{curr.false_child.node_id} '
                    f'[label="False (Alternative)", color="#C62828", fontcolor="#C62828", style=dashed];'
                )
                traverse(curr.false_child)

        traverse(self.root)
        lines.append("}")
        return "\n".join(lines)