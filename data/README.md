# Panduan Dataset — Tugas 2 (Data Product)

Folder ini digunakan untuk menempatkan dataset yang dipakai dalam dashboard analitik.

> **PENTING:** Jangan pernah melakukan `git commit` atau `git push` file dataset besar (>100MB) langsung ke repository GitHub! File data besar harus diabaikan melalui `.gitignore`.

---

## Informasi Dataset Kelompok

- **Nama Dataset:** 1.3M LinkedIn Jobs & Skills (2024)
- **Sumber Data:** https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024
- **Ukuran File Mentah:** 1 GB
- **Jumlah Baris:** 1.348.454 Baris
- **Format File:** CSV

---

## Instruksi Pengunduhan & Penyiapan Data

Dataset dapat diunduh secara otomatis menggunakan Kaggle CLI (pastikan library `kaggle` sudah terpasang dan file kredensial `~/.kaggle/kaggle.json` tersedia):

```bash
pip install kaggle
kaggle datasets download -d asaniczka/1-3m-linkedin-jobs-and-skills-2024 -p data/ --unzip
```
Atau unduh secara manual melalui halaman resmi Kaggle: https://www.kaggle.com/datasets/asaniczka/1-3m-linkedin-jobs-and-skills-2024

Ekstrak file hasil unduhan ke folder `data/`. File utama yang digunakan:

- `data/linkedin_job_postings.csv`
- `data/job_skills.csv`

---

## Skema Struktur Kolom Data

| Nama Kolom | Tipe Data | Deskripsi Makna Bisnis |
|------------|:---------:|------------------------|
| `job_link` | Utf8 | URL unik lowongan sebagai kunci relasi antar tabel |
| `job_tittle` | Utf8 | Judul posisi pekerjaan yang dibuka |
| `company` | Utf8 | Nama perusahaan yang membuka lowongan |
| `job_location` | Utf8 | Lokasi detail pekerjaan (kota/negara bagian) |
| `search_country` | Utf8 | Negara lokasi pencarian lowongan |
| `search_city` | Utf8 | Kota lokasi pencarian lowongan |
| `first_seen` | Date | Tanggal lowongan pertama kali terdeteksi |
| `last_processed_time` | Datetime | Waktu terakhir data lowongan diproses |
| `job_level` | Utf8 | Tingkat senioritas jabatan (misal: Associate, Mid senior) |
| `job_type` | Utf8 | Sistem kerja (Onsite, Remote, Hybrid) |
| `job_skills` | Utf8 | Daftar keterampilan (skills) yang diminta pada lowongan |