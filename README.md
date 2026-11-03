# Single-Classification Ripple Down Rules (SCRDR) Expert System

Sistem pakar berbasis **Ripple Down Rules (RDR)** interaktif yang dirancang untuk membantu pakar memberikan rekomendasi bagi konsumen secara inkremental. Sistem mendukung atribut biner (boolean), numerikal, serta mematuhi prinsip **Open World Assumption (OWA)**.

## 📌 Fitur Utama

- **Struktur Binary Tree RDR**:
  - **Anak Kanan (*true-child*)**: Cabang perkecualian (*exception*) saat kondisi terpenuhi.
  - **Anak Kiri (*false-child*)**: Cabang alternatif saat kondisi tidak terpenuhi (mempertahankan kesimpulan valid sebelumnya).
- **Inference with Rule Override**: Kesimpulan akhir sistem adalah kesimpulan terakhir yang bernilai `True` sepanjang jalur evaluasi.
- **Open World Assumption (OWA)**: Ketiadaan atribut pada data konsumen dianggap *unknown* (bukan diasumsikan `False` / `Not`).
- **Difference Matrix**: Menampilkan variabel pembeda signifikan antara kasus baru dengan *cornerstone case* dari rule yang hendak dianulir.
- **Knowledge Base Retesting**: Pengujian ulang seluruh kasus acuan (*cornerstone cases*) ke pohon aturan untuk memantau konsistensi basis pengetahuan.
- **Dukungan 2 Dataset**:
  1. *Loan Approval Dataset* (Domain Finansial / Kredit)
  2. *Telco Customer Churn Dataset* (Domain Retensi Konsumen)

---

## 📂 Struktur Direktori

```text
rdr-expert-system/
├── data/
│   ├── raw/                  # Tempat file dataset CSV mentah
│   │   ├── loan_approval_dataset.csv
│   │   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
│   └── processed/            # Hasil pembersihan data (terbentuk otomatis)
│       ├── loan_approval_clean.csv
│       └── telco_churn_clean.csv
├── src/
│   ├── core/                 # Condition, RDRNode, dan RDRTree
│   ├── expert/               # Ekstraksi pembeda & validator retest
│   └── utils/                # Preprocessing & loader dataset
├── app/
│   └── app.py                # Antarmuka CLI interaktif
├── tests/                    # Unit testing (OWA, inferensi, knowledge update)
├── requirements.txt
└── README.md

```

---

## 🚀 Panduan Menjalankan Sistem

### 1. Prasyarat & Instalasi Dependensi

Pastikan Python 3.10+ telah terpasang. Pasang dependensi yang dibutuhkan:

```bash
pip install pandas
```

### 2. Penyiapan Dataset Mentah

Letakkan kedua file dataset berikut ke dalam folder `data/raw/`:

* `loan_approval_dataset.csv`
* `WA_Fn-UseC_-Telco-Customer-Churn.csv`

### 3. Pra-pemrosesan Data (Cukup Sekali)

Jalankan skrip pra-pemrosesan untuk membersihkan spasi nama kolom, menghapus ID unik, dan memformat data sesuai prinsip OWA:

```bash
python -m src.utils.preprocess
```

*File bersih akan otomatis tersimpan di folder `data/processed/`.*

### 4. Menjalankan Pengujian Unit (Opsional)

Jalankan seluruh unit test untuk memverifikasi logika OWA dan penelusuran pohon:

```bash
python -m unittest discover tests
```

### 5. Menjalankan Aplikasi CLI Interaktif

Jalankan aplikasi utama:

```bash
python -m app.app
```

## 🎮 Cara Penggunaan di CLI

### 1. Memilih Domain Dataset
Saat aplikasi pertama kali dijalankan, Anda akan diminta memilih salah satu dari dua domain dataset:
* **Pilihan `1` (Telco Customer Churn)**: Pemenuhan aturan default berbasis **True-False / Boolean murni** (kesimpulan awal root: `No`).
* **Pilihan `2` (Loan Approval)**: Pemenuhan **numerikal** (kesimpulan awal root: `Rejected`).

---

### 2. Navigasi Menu Utama

Setelah memilih domain, sistem menampilkan 5 opsi menu:

```text
MENU UTAMA:
1. Jalankan Simulasi Kasus dari Dataset
2. Input Kasus Konsumen Manual
3. Uji Ulang Basis Pengetahuan (Knowledge Retest)
4. Ganti Dataset (Telco Churn / Loan Approval)
5. Keluar

```

---

### 3. Alur Interaksi Pengambilan Keputusan (Menu 1 & 2)

Setiap kali data konsumen dievaluasi oleh sistem, alur interaksi pakar berjalan sebagai berikut:

1. **Inferensi Sistem**:
* Sistem membaca atribut kasus dan menelusuri pohon keputusan (*RDR Tree*).
* Menampilkan ringkasan data konsumen, label acuan dataset (*Ground Truth*), dan **Rekomendasi Sistem Saat Ini** beserta ID simpul aktif.


2. **Validasi oleh Pakar (`y/n`)**:
* **Setuju (`y`)**: Struktur pohon dipertahankan, proses selesai untuk kasus tersebut.
* **Tidak Setuju (`n`)**: Sistem memulai alur penambahan aturan perkecualian baru (*exception rule*).


3. **Perumusan Rekomendasi Baru**:
* Pakar memasukkan kesimpulan/keputusan yang benar (cukup tekan **Enter** langsung jika ingin menyetujui rekomendasi sesuai *Ground Truth*).


4. **Seleksi Variabel Pembeda (*Difference Matrix*)**:
* Sistem otomatis membandingkan kasus baru dengan kasus acuan (*cornerstone case*) dari aturan yang hendak dianulir, dengan tetap menerapkan prinsip **Open World Assumption (OWA)**.
* Pakar memilih nomor variabel pembeda yang signifikan (bisa lebih dari satu, contoh: ketik `1` atau `1,2`).
* Sistem otomatis menempatkan simpul baru pada cabang yang tepat:
* **Anak Kanan (*true-child*)**: Jika kondisi aturan sebelumnya terpenuhi (perkecualian/spesialisasi).
* **Anak Kiri (*false-child*)**: Jika kondisi aturan sebelumnya gagal/tidak terpenuhi (alternatif).





---

### 4. Input Kasus Konsumen Manual (Menu 2)

Jika ingin menguji skenario kustom, masukkan atribut dengan format `kunci=nilai` dipisahkan koma:

* **Format Boolean**: `SeniorCitizen=True, Partner=False, PaperlessBilling=True`
* **Format Numerik**: `cibil_score=750, loan_amount=10000000, income_annum=8500000`
* *Catatan OWA*: Variabel yang tidak dituliskan otomatis diperlakukan sebagai **tidak diketahui (*unknown*)**, bukan bernilai `False`.

---

### 5. Pengujian Ulang Basis Pengetahuan (Menu 3 - Knowledge Retest)

Digunakan kapan saja untuk memverifikasi kestabilan pohon keputusan:

* Menguji kembali seluruh *cornerstone cases* yang tersimpan ke dalam struktur pohon terbaru.
* Menampilkan ringkasan jumlah kasus yang konsisten, kasus yang mengalami perubahan output (*side effect*), serta persentase konsistensi aturan.