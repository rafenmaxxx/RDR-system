import unittest
from src.core.condition import Condition
from src.core.rdr_tree import RippleDownRulesSystem
from src.expert.difference import DifferenceExtractor
from src.expert.validator import KnowledgeValidator

class TestKnowledgeUpdateAndRetest(unittest.TestCase):
    def test_cornerstone_case_retest(self):
        """
        Menguji apakah modul validator dapat melacak seluruh cornerstone cases
        dan memverifikasi apakah kesimpulan historisnya konsisten atau berubah.
        """
        rdr = RippleDownRulesSystem(default_conclusion="Default_Tolak")
        validator = KnowledgeValidator(rdr)

        # Kasus 1: Membentuk rule pertama
        case_1 = {"member": True}
        ctx_1 = rdr.infer(case_1)
        
        # Instance pertama dibandingkan dengan nothing (None)
        diff_1 = DifferenceExtractor.extract_candidates(case_1, ctx_1["last_satisfied_node"].cornerstone_case)
        self.assertTrue(len(diff_1) > 0)
        
        rdr.add_rule(ctx_1, [Condition("member", "==", True)], "Diskon_10%", case_1)

        # Validasi kasus 1
        summary_1 = validator.get_validation_summary()
        self.assertEqual(summary_1["total_tested"], 1)
        self.assertEqual(summary_1["consistent_count"], 1)

        # Kasus 2: Member tapi total belanja > 1.000.000 -> Diskon 20%
        case_2 = {"member": True, "belanja": 1500000}
        ctx_2 = rdr.infer(case_2)
        
        diff_2 = DifferenceExtractor.extract_candidates(case_2, ctx_2["last_satisfied_node"].cornerstone_case)
        # diff_2 harus memuat variabel belanja
        self.assertTrue(any(c.attribute == "belanja" for c in diff_2))

        rdr.add_rule(ctx_2, [Condition("belanja", ">", 1000000)], "Diskon_20%", case_2)

        # Uji ulang seluruh kasus yang ada
        summary_2 = validator.get_validation_summary()
        self.assertEqual(summary_2["total_tested"], 2)
        # Kedua kasus acuan harus tetap menghasilkan kesimpulannya masing-masing
        self.assertEqual(summary_2["consistent_count"], 2)
        self.assertEqual(summary_2["consistency_rate"], 100.0)

if __name__ == "__main__":
    unittest.main()