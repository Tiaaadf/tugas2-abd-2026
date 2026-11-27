from pathlib import Path
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

POSTINGS_CSV = RAW_DIR / "linkedin_job_postings.csv"
SKILLS_CSV = RAW_DIR / "job_skills.csv"

POSTINGS_PARQUET = PROCESSED_DIR / "linkedin_job_postings.parquet"
SKILLS_PARQUET = PROCESSED_DIR / "job_skills.parquet"


def prepare_postings() -> None:
    """Membersihkan linkedin_job_postings.csv dan menyimpannya ke Parquet."""
    if not POSTINGS_CSV.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {POSTINGS_CSV}")

    print(f"Membaca {POSTINGS_CSV.name} secara lazy dengan Polars...")
    lf = pl.scan_csv(POSTINGS_CSV, ignore_errors=True)

    kolom_pakai = [
        "job_link",
        "job_title",
        "company",
        "job_location",
        "first_seen",
        "search_city",
        "search_country",
        "search_position",
        "job_level",
        "job_type",
    ]
    kolom_tersedia = [c for c in kolom_pakai if c in lf.collect_schema().names()]

    lf_clean = (
        lf.select(kolom_tersedia)
        .with_columns([
            pl.col("job_link").cast(pl.String).str.strip_chars(),
            pl.col("job_title").cast(pl.String).str.strip_chars(),
            pl.col("company").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("job_location").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("search_city").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("search_country").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("job_level").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("job_type").cast(pl.String).str.strip_chars().fill_null("Unknown"),
            pl.col("first_seen").cast(pl.String).str.to_date(strict=False),
        ])
        .filter(
            pl.col("job_link").is_not_null()
            & (pl.col("job_link") != "")
            & pl.col("job_title").is_not_null()
            & (pl.col("job_title") != "")
        )
        .unique(subset=["job_link"], keep="first")
    )

    df_clean = lf_clean.collect()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.write_parquet(POSTINGS_PARQUET, compression="zstd")

    size_mb = POSTINGS_PARQUET.stat().st_size / (1024 * 1024)
    print(f"Selesai postings: {df_clean.height:,} baris -> {POSTINGS_PARQUET.name} ({size_mb:.2f} MB)")


def prepare_skills() -> None:
    """Membersihkan job_skills.csv dan menyimpannya ke Parquet."""
    if not SKILLS_CSV.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {SKILLS_CSV}")

    print(f"Membaca {SKILLS_CSV.name} secara lazy dengan Polars...")
    lf = pl.scan_csv(SKILLS_CSV, ignore_errors=True)

    lf_clean = (
        lf.select(["job_link", "job_skills"])
        .with_columns([
            pl.col("job_link").cast(pl.String).str.strip_chars(),
            pl.col("job_skills").cast(pl.String).str.strip_chars(),
        ])
        .filter(
            pl.col("job_link").is_not_null()
            & (pl.col("job_link") != "")
            & pl.col("job_skills").is_not_null()
            & (pl.col("job_skills") != "")
        )
        .unique(subset=["job_link"], keep="first")
    )

    df_clean = lf_clean.collect()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.write_parquet(SKILLS_PARQUET, compression="zstd")

    size_mb = SKILLS_PARQUET.stat().st_size / (1024 * 1024)
    print(f"Selesai skills: {df_clean.height:,} baris -> {SKILLS_PARQUET.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    prepare_postings()
    prepare_skills()