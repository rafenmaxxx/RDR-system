from typing import Any, Dict, List
from src.core.rdr_tree import RippleDownRulesSystem

class KnowledgeValidator:
    """
    Modul untuk validasi dan pengujian ulang basis pengetahuan (knowledge base update).
    Instance-instance pembentuk rule diuji kembali ke pohon yang ada.
    """

    def __init__(self, rdr_system: RippleDownRulesSystem):
        self.rdr = rdr_system

    def validate_all_cornerstones(self) -> List[Dict[str, Any]]:
        """
        Menguji kembali semua cornerstone case yang tersimpan di dalam registry pohon.
        Mengecek apakah kesimpulan saat ini masih sama dengan kesimpulan yang diharapkan (expected)
        atau telah berubah akibat penambahan rule-rule baru setelahnya.
        """
        report: List[Dict[str, Any]] = []

        for node_id, case, expected_conclusion in self.rdr.cornerstone_registry:
            inference_result = self.rdr.infer(case)
            current_output = inference_result["conclusion"]
            
            is_consistent = (current_output == expected_conclusion)

            report.append({
                "origin_node_id": node_id,
                "case_data": case,
                "expected_conclusion": expected_conclusion,
                "current_conclusion": current_output,
                "is_consistent": is_consistent,
                "last_satisfied_node_id": inference_result["last_satisfied_node"].node_id
            })

        return report

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Menyajikan ringkasan statistik konsistensi basis pengetahuan.
        """
        details = self.validate_all_cornerstones()
        total_cases = len(details)
        consistent_cases = sum(1 for item in details if item["is_consistent"])
        inconsistent_cases = total_cases - consistent_cases

        return {
            "total_tested": total_cases,
            "consistent_count": consistent_cases,
            "inconsistent_count": inconsistent_cases,
            "consistency_rate": (consistent_cases / total_cases * 100.0) if total_cases > 0 else 100.0,
            "details": details
        }