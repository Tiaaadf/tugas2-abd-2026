from pathlib import Path
from typing import Dict, Union
import duckdb
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def get_data_paths() -> Dict[str, Path]:
    """Mengembalikan path file Parquet hasil preprocessing."""
    return {
        "postings": PROCESSED_DIR / "linkedin_job_postings.parquet",
        "skills": PROCESSED_DIR / "job_skills.parquet",
    }


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Membuat koneksi DuckDB in-memory untuk analitik Parquet."""
    return duckdb.connect(database=":memory:")


def format_angka_ringkas(angka: Union[int, float]) -> str:
    """Memformat angka besar menjadi notasi ringkas (K, M, B)."""
    if angka is None:
        return "0"
    abs_angka = abs(angka)
    if abs_angka >= 1_000_000_000:
        return f"{angka / 1_000_000_000:.2f} B"
    if abs_angka >= 1_000_000:
        return f"{angka / 1_000_000:.2f} M"
    if abs_angka >= 1_000:
        return f"{angka / 1_000:.1f} K"
    return f"{angka:,.0f}"


def format_persen(nilai: Union[int, float]) -> str:
    """Memformat persentase dengan 1 angka di belakang koma."""
    if nilai is None:
        return "0.0%"
    return f"{nilai:.1f}%"


def load_parquet_aman(filepath_glob: str) -> pl.DataFrame:
    """Membaca file Parquet menggunakan Polars lazy evaluation."""
    return pl.scan_parquet(filepath_glob).collect()