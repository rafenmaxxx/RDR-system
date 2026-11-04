import os
import sys
from typing import Any, Dict, List, Optional
from src.core.condition import Condition, Case
from src.core.rdr_tree import RippleDownRulesSystem
from src.expert.difference import DifferenceExtractor
from src.expert.validator import KnowledgeValidator
from src.utils.data_loader import DataLoader


class RDRInteractiveCLI:
    def __init__(self):
        print("=" * 65)
        print("  SISTEM PAKAR REKOMENDASI KONSUMEN BERBASIS RDR (SCRDR)")
        print("  Mendukung: Biner/Boolean, Numerikal, & Prinsip OWA")
        print("=" * 65)

        # 1. Pilih preset dataset (No 1: Telco, No 2: Loan)
        config = self._choose_dataset_profile()
        self.dataset_config = config

        self.rdr = RippleDownRulesSystem(default_conclusion=config["default_root"])
        self.validator = KnowledgeValidator(self.rdr)
        print(f"\n[OK] Sesi dimulai untuk Domain: {config['name']}")
        print(f"[OK] Root Tree diinisialisasi dengan Kesimpulan Default: '{config['default_root']}'\n")

    def _choose_dataset_profile(self) -> Dict[str, Any]:
        """
        Menyediakan opsi pemilihan dataset:
        1 = Telco Churn (True-False)
        2 = Loan Approval (Numerikal)
        """
        print("\nPILIH DOMAIN DATASET KASUS:")
        print("1. Telco Customer Churn Dataset (True-False / Boolean)")
        print("2. Loan Approval Dataset (Numerikal)")
        print("-" * 50)

        while True:
            choice = input("Pilih dataset (1 atau 2): ").strip()
            if choice == "1":
                return {
                    "name": "Telco Customer Churn (True-False)",
                    "file_path": "data/processed/telco_churn_clean.csv",
                    "raw_fallback": "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv",
                    "target_column": "Churn",
                    "default_root": "No"
                }
            elif choice == "2":
                return {
                    "name": "Loan Approval (Numerikal)",
                    "file_path": "data/processed/loan_approval_clean.csv",
                    "raw_fallback": "data/raw/loan_approval_dataset.csv",
                    "target_column": "loan_status",
                    "default_root": "Rejected"
                }
            else:
                print("[!] Pilihan tidak valid. Silakan masukkan angka 1 atau 2.")

    def run(self):
        while True:
            print("-" * 50)
            print(f"MENU UTAMA ({self.dataset_config['name']}):")
            print("1. Jalankan Simulasi Kasus dari Dataset")
            print("2. Input Kasus Konsumen Manual")
            print("3. Uji Ulang Basis Pengetahuan (Knowledge Retest)")
            print("4. Tampilkan Struktur Pohon Keputusan (Tree View)")
            print("5. Ganti Dataset (Telco Churn / Loan Approval)")
            print("6. Keluar")
            print("-" * 50)

            menu = input("Pilih menu (1-6): ").strip()

            if menu == "1":
                self._run_dataset_simulation()
            elif menu == "2":
                case = self._input_case_manual()
                if case:
                    self._process_case_interaction(case)
            elif menu == "3":
                self._show_validation_report()
            elif menu == "4":
                self._show_tree_structure()
            elif menu == "5":
                self.__init__()
            elif menu == "6":
                print("\nTerima kasih telah menggunakan sistem pakar RDR.")
                sys.exit(0)
            else:
                print("[!] Pilihan tidak dikenali. Masukkan angka 1-6.")

    def _show_tree_structure(self):
        print("\n" + "=" * 65)
        print("         STRUKTUR POHON KEPUTUSAN RDR SAAT INI")
        print("=" * 65)
        print(self.rdr.get_tree_text())
        print("=" * 65)

        export_dot = input("\nSimpan kode diagram Graphviz (.dot) untuk laporan? (y/n): ").strip().lower()
        if export_dot in {"y", "yes"}:
            dot_code = self.rdr.export_graphviz_dot()
            filename = f"rdr_tree_{self.dataset_config['name'].lower().replace(' ', '_')}.dot"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(dot_code)
            print(f"[OK] Berkas DOT berhasil disimpan sebagai '{filename}'.")
            print("     Anda dapat memvisualisasikannya di https://dreampuf.github.io/GraphvizOnline")

    def _run_dataset_simulation(self):
        """
        Membaca dataset baris per baris dan menyimulasikannya ke antarmuka pakar.
        Menyediakan opsi pembatasan jumlah kasus (misal: 10 kasus) untuk pengujian pohon.
        """
        file_path = self.dataset_config["file_path"]

        if not os.path.exists(file_path):
            fallback = self.dataset_config.get("raw_fallback")
            if fallback and os.path.exists(fallback):
                file_path = fallback
            else:
                print(f"[!] File dataset tidak ditemukan di '{file_path}' maupun '{fallback}'.")
                print("    Jalankan skrip 'py -m src.utils.preprocess' terlebih dahulu.")
                return

        try:
            records = DataLoader.load_from_csv(
                file_path, 
                target_column=self.dataset_config["target_column"]
            )
            total_records = len(records)
            print(f"\n[OK] Berhasil memuat total {total_records} baris data dari '{file_path}'.")
        except Exception as e:
            print(f"[!] Gagal memuat dataset: {e}")
            return

        # --- OPSI PEMBATASAN KASUS (PENGUJIAN CEPAT) ---
        print("\nPENGATURAN KASUS UNTUK PENGUJIAN POHON:")
        print("1. Jalankan 10 Kasus Pertama Saja (Sangat Direkomendasikan untuk Verifikasi)")
        print("2. Tentukan Jumlah Kasus Sendiri (Kustom)")
        print("3. Jalankan Seluruh Data")
        opt = input("Pilihan opsi (1/2/3) [Default 1]: ").strip()

        if opt == "2":
            custom_n = input("Masukkan jumlah kasus yang ingin diuji (misal: 5 atau 20): ").strip()
            limit = int(custom_n) if custom_n.isdigit() and int(custom_n) > 0 else 10
        elif opt == "3":
            limit = total_records
        else:
            limit = min(10, total_records)  # Default 10 kasus

        records_to_run = records[:limit]
        print(f"\n[INFO] Menjalankan simulasi untuk {len(records_to_run)} kasus terpilih...\n")

        for idx, (case, ground_truth) in enumerate(records_to_run, start=1):
            print(f"\n==================== KASUS KE-{idx} DARI {len(records_to_run)} ====================")
            self._process_case_interaction(case, ground_truth)

            # Jika belum kasus terakhir, tanyakan apakah ingin lanjut
            if idx < len(records_to_run):
                nav = input("\nLanjut ke kasus berikutnya? (y = ya / n = kembali ke menu): ").strip().lower()
                if nav not in {"y", "yes"}:
                    print("\n[i] Simulasi dihentikan. Struktur pohon saat ini tetap tersimpan.")
                    break
            else:
                print(f"\n[✓] Seluruh {len(records_to_run)} kasus pengujian telah selesai dievaluasi.")

    def _input_case_manual(self) -> Case:
        print("\n--- INPUT KASUS KONSUMEN MANUAL (Format: key=value) ---")
        print("Contoh Boolean  : SeniorCitizen=True, Partner=False, PaperlessBilling=True")
        print("Contoh Numerik  : cibil_score=750, loan_amount=10000000")
        print("(Atribut yang tidak dituliskan dianggap TIDAK DIKETAHUI sesuai prinsip OWA)")
        
        raw_in = input("Data kasus (pisahkan koma): ").strip()
        if not raw_in:
            print("[!] Input dibatalkan.")
            return {}

        case: Case = {}
        for item in raw_in.split(","):
            if "=" in item:
                k, v = item.split("=", 1)
                k = k.strip()
                v = v.strip()

                # Konversi biner
                if v.lower() in {"true", "yes", "1"}:
                    case[k] = True
                elif v.lower() in {"false", "no", "0"}:
                    case[k] = False
                else:
                    # Konversi numerik vs string
                    try:
                        case[k] = float(v) if "." in v else int(v)
                    except ValueError:
                        case[k] = v
        return case

    def _process_case_interaction(self, case: Case, ground_truth: Optional[str] = None):
        """
        Alur interaksi RDR:
        1. Inferensi pohon saat ini.
        2. Tampilkan kesimpulan sistem dan ground truth.
        3. Konfirmasi pakar (Setuju / Tidak).
        4. Jika tidak setuju, tampilkan variabel pembeda vs cornerstone case.
        5. Bentuk cabang baru (kanan atau kiri).
        """
        print("\nDATA KONSUMEN:")
        for k, v in case.items():
            print(f"  * {k}: {v}")
        if ground_truth is not None:
            print(f"  * [Ground Truth Label]: {ground_truth}")

        inference_ctx = self.rdr.infer(case)
        system_conclusion = inference_ctx["conclusion"]
        last_satisfied = inference_ctx["last_satisfied_node"]

        print(f"\n--> [REKOMENDASI SISTEM]: {system_conclusion} (Node {last_satisfied.node_id})")

        agreement = input("Apakah Anda sebagai Pakar SETUJU dengan rekomendasi ini? (y/n): ").strip().lower()

        if agreement in {"y", "yes"}:
            print("[✓] Rekomendasi disetujui. Tree tidak diubah.")
            return

        print("\n[!] Pakar tidak setuju. Menyiapkan aturan perkecualian baru...")
        suggested_label = ground_truth if ground_truth else ""
        prompt_label = f"Masukkan Rekomendasi Baru Pakar [{suggested_label}]: " if suggested_label else "Masukkan Rekomendasi Baru Pakar: "
        new_conclusion = input(prompt_label).strip()
        if not new_conclusion and suggested_label:
            new_conclusion = suggested_label

        cornerstone = last_satisfied.cornerstone_case
        candidates = DifferenceExtractor.extract_candidates(case, cornerstone)

        selected_conditions: List[Condition] = []
        if not candidates:
            print("[!] Tidak terdeteksi perbedaan otomatis dengan cornerstone case.")
            attr = input("Ketik nama atribut pembeda: ").strip()
            op = input("Operator (==, !=, >, <, >=, <=): ").strip()
            val = input("Nilai: ").strip()
            selected_conditions = [Condition(attr, op, val)]
        else:
            print("\nKANDIDAT VARIABEL PEMBEDA (Kasus Baru vs Kasus Acuan):")
            for idx, cond in enumerate(candidates, start=1):
                print(f"  [{idx}] {cond}")

            print("\nPilih nomor kondisi pembeda yang signifikan (pisahkan koma jika > 1, misal: 1 atau 1,2):")
            selection = input("Nomor pilihan: ").strip()

            for item in selection.split(","):
                item = item.strip()
                if item.isdigit():
                    pos = int(item) - 1
                    if 0 <= pos < len(candidates):
                        selected_conditions.append(candidates[pos])

            if not selected_conditions:
                print("[i] Tidak ada nomor yang dipilih. Mengambil kandidat pertama secara default.")
                selected_conditions = [candidates[0]]

        new_node = self.rdr.add_rule(
            inference_context=inference_ctx,
            conditions=selected_conditions,
            new_conclusion=new_conclusion,
            new_case=case
        )

        branch_name = "ANAK KANAN (Exception / Kondisi True)" if inference_ctx["last_eval_status"] else "ANAK KIRI (Alternatif / Kondisi False)"
        print(f"\n[SUKSES] Node {new_node.node_id} berhasil dibuat pada cabang {branch_name}!")
        print(f"         IF {' AND '.join(str(c) for c in selected_conditions)} THEN '{new_conclusion}'")

    def _show_validation_report(self):
        print("\n" + "=" * 65)
        print("  LAPORAN PENGUJIAN ULANG KNOWLEDGE BASE (KNOWLEDGE RETEST)")
        print("=" * 65)

        summary = self.validator.get_validation_summary()
        print(f"Total Kasus Acuan (Cornerstones) : {summary['total_tested']}")
        print(f"Kasus Konsisten                  : {summary['consistent_count']}")
        print(f"Kasus Mengalami Perubahan Output : {summary['inconsistent_count']}")
        print(f"Tingkat Konsistensi              : {summary['consistency_rate']:.2f}%\n")

        if summary["details"]:
            print(f"{'Node ID':<9} | {'Expected':<18} | {'Output Sekarang':<18} | {'Status'}")
            print("-" * 65)
            for item in summary["details"]:
                status = "KONSISTEN" if item["is_consistent"] else "BERUBAH"
                print(f"{item['origin_node_id']:<9} | {item['expected_conclusion']:<18} | {item['current_conclusion']:<18} | {status}")
        else:
            print("[i] Belum ada kasus acuan yang terdaftar pada pohon.")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    app = RDRInteractiveCLI()
    app.run()