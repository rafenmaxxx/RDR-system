import unittest
from src.core.condition import Condition

class TestOpenWorldAssumption(unittest.TestCase):
    def test_missing_attribute_does_not_equal_false(self):
        """
        Menguji prinsip OWA: jika atribut tidak ada di dalam kasus,
        kondisi tidak terpenuhi (False), TETAPI bukan berarti nilainya dianggap False.
        """
        # Kondisi: butuh 'riwayat_kredit_buruk' == False
        cond_not_bad = Condition("riwayat_kredit_buruk", "==", False)

        # Kasus A: Atribut eksplisit bernilai False
        case_with_explicit_false = {"riwayat_kredit_buruk": False}
        self.assertTrue(cond_not_bad.evaluate(case_with_explicit_false))

        # Kasus B: Atribut TIDAK ADA sama sekali di dalam kasus (Unknown)
        # Sesuai OWA: ga ada bukan berarti not / false
        case_missing_attr = {"penghasilan": 10000000}
        self.assertFalse(
            cond_not_bad.evaluate(case_missing_attr),
            "Berdasarkan OWA, atribut yang hilang tidak boleh diasumsikan bernilai False."
        )

    def test_missing_attribute_numeric_condition(self):
        """
        Menguji OWA pada operator numerik:
        Jika data numerik tidak ada atau None, kondisi numerik harus mengembalikan False.
        """
        cond_numeric = Condition("skor_kredit", ">", 600)

        case_without_score = {"nama": "Budi"}
        self.assertFalse(cond_numeric.evaluate(case_without_score))

        case_with_none_score = {"skor_kredit": None}
        self.assertFalse(cond_numeric.evaluate(case_with_none_score))

        case_valid_score = {"skor_kredit": 750}
        self.assertTrue(cond_numeric.evaluate(case_valid_score))

if __name__ == "__main__":
    unittest.main()