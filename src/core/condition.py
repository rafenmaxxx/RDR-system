from typing import Any, Dict, Optional

Case = Dict[str, Any]

class Condition:
    """
    Merepresentasikan satu kondisi predikat pada sebuah rule RDR.
    Mendukung nilai boolean/biner dan numerikal.
    Menerapkan prinsip Open World Assumption (OWA).
    """

    VALID_OPERATORS = {"==", "!=", ">", "<", ">=", "<="}

    def __init__(self, attribute: str, operator: str, value: Any):
        if operator not in self.VALID_OPERATORS:
            raise ValueError(f"Operator '{operator}' tidak didukung. Gunakan salah satu dari {self.VALID_OPERATORS}")
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def evaluate(self, case: Case) -> bool:
        """
        Mengevaluasi kondisi terhadap sebuah instance kasus.
        
        Prinsip OWA (Open World Assumption):
        Jika atribut tidak ada di dalam kasus (atau bernilai None), artinya informasi
        tersebut 'tidak diketahui' (unknown), BUKAN berarti 'False' atau 'Not'.
        Oleh karena itu, kondisi yang mensyaratkan atribut tersebut TIDAK BISA terpenuhi (return False).
        """
        if self.attribute not in case or case[self.attribute] is None:
            return False

        case_val = case[self.attribute]

        try:
            # Evaluasi untuk atribut numerikal
            if self.operator in {">", "<", ">=", "<="}:
                num_case = float(case_val)
                num_target = float(self.value)
                if self.operator == ">":
                    return num_case > num_target
                elif self.operator == "<":
                    return num_case < num_target
                elif self.operator == ">=":
                    return num_case >= num_target
                elif self.operator == "<=":
                    return num_case <= num_target

            # Evaluasi untuk atribut kesetaraan (boolean / string / kategorikal / numerikal)
            elif self.operator == "==":
                return case_val == self.value
            elif self.operator == "!=":
                return case_val != self.value

        except (ValueError, TypeError):
            # Jika tipe data tidak dapat dikomparasi secara valid
            return False

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribute": self.attribute,
            "operator": self.operator,
            "value": self.value
        }

    def __repr__(self) -> str:
        return f"{self.attribute} {self.operator} {self.value}"