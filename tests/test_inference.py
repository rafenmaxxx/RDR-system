import unittest
from src.core.condition import Condition
from src.core.rdr_tree import RippleDownRulesSystem

class TestRDRInference(unittest.TestCase):
    def setUp(self):
        # Inisialisasi pohon dengan satu aturan awal (t -> Tolak)
        self.rdr = RippleDownRulesSystem(default_conclusion="Tolak")

    def test_root_default_conclusion(self):
        """
        Menguji kasus pertama kali saat tree hanya berisi root default.
        """
        case = {"umur": 25}
        result = self.rdr.infer(case)
        self.assertEqual(result["conclusion"], "Tolak")
        self.assertEqual(result["last_satisfied_node"].node_id, self.rdr.root.node_id)

    def test_true_child_branching_and_override(self):
        """
        Menguji penambahan cabang kanan (anak kanan / true-child).
        Jika kondisi terpenuhi, kesimpulan default dianulir oleh kesimpulan baru.
        """
        case_1 = {"bekerja": True}
        ctx_1 = self.rdr.infer(case_1)

        # Pakar menambahkan rule: IF bekerja == True THEN Terima
        rule_1 = [Condition("bekerja", "==", True)]
        self.rdr.add_rule(ctx_1, rule_1, "Terima", case_1)

        # Uji kasus yang memenuhi kondisi baru
        new_result = self.rdr.infer({"bekerja": True})
        self.assertEqual(new_result["conclusion"], "Terima")

    def test_false_child_branching_preserves_last_conclusion(self):
        """
        Menguji penambahan cabang kiri (anak kiri / false-child).
        Jika kondisi tidak terpenuhi, kesimpulan tidak berubah ke rule yang gagal.
        """
        # Bentuk rule level 1 (anak kanan dari root)
        case_1 = {"bekerja": True}
        ctx_1 = self.rdr.infer(case_1)
        self.rdr.add_rule(ctx_1, [Condition("bekerja", "==", True)], "Terima", case_1)

        # Bentuk perkecualian level 2: IF skor_kredit <= 500 THEN Tinjau
        case_2 = {"bekerja": True, "skor_kredit": 450}
        ctx_2 = self.rdr.infer(case_2)
        self.rdr.add_rule(ctx_2, [Condition("skor_kredit", "<=", 500)], "Tinjau", case_2)

        # Kasus 3: Bekerja True, tapi skor_kredit > 500 (misal 700)
        # Jalur: Root (True) -> Rule 1 (True, kesimpulan: Terima) -> Rule 2 (False, cabang kiri None)
        # Kesimpulan akhir harus tetap 'Terima' (kesimpulan valid terakhir)
        case_3 = {"bekerja": True, "skor_kredit": 700}
        res_3 = self.rdr.infer(case_3)
        self.assertEqual(res_3["conclusion"], "Terima")

if __name__ == "__main__":
    unittest.main()