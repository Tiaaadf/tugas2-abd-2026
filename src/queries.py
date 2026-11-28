
from pathlib import Path

import duckdb
import polars as pl


# menentukan lokasi file parquet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTINGS_PATH = PROJECT_ROOT / "data" / "processed" / "linkedin_job_postings.parquet"
SKILLS_PATH = PROJECT_ROOT / "data" / "processed" / "job_skills.parquet"


def _execute_to_polars(
    con: duckdb.DuckDBPyConnection,
    sql: str
) -> pl.DataFrame:
    """Menjalankan query DuckDB dan mengubah hasilnya menjadi Polars DataFrame."""
    try:
        return con.sql(sql).pl()
    except Exception:
        return pl.from_arrow(con.execute(sql).arrow())


def _register_parquet(con: duckdb.DuckDBPyConnection) -> None:
    """Mendaftarkan file Parquet sebagai view di DuckDB."""

    if not POSTINGS_PATH.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {POSTINGS_PATH}")

    if not SKILLS_PATH.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {SKILLS_PATH}")

    postings_path = POSTINGS_PATH.as_posix().replace("'", "''")
    skills_path = SKILLS_PATH.as_posix().replace("'", "''")

    con.execute(f"""
        CREATE OR REPLACE VIEW postings AS
        SELECT * FROM read_parquet('{postings_path}')
    """)

    con.execute(f"""
        CREATE OR REPLACE VIEW skills AS
        SELECT * FROM read_parquet('{skills_path}')
    """)


def query_ringkasan_lowongan(
    con: duckdb.DuckDBPyConnection
) -> pl.DataFrame:
    """Menghitung ringkasan umum data lowongan pekerjaan."""

    _register_parquet(con)

    sql = """
        SELECT
            COUNT(*) AS total_lowongan,
            COUNT(DISTINCT company) FILTER (
                WHERE company != 'Unknown'
            ) AS total_perusahaan,
            COUNT(DISTINCT job_location) FILTER (
                WHERE job_location != 'Unknown'
            ) AS total_lokasi,
            COUNT(DISTINCT search_country) FILTER (
                WHERE search_country != 'Unknown'
            ) AS total_negara
        FROM postings;
    """

    return _execute_to_polars(con, sql)


def query_distribusi_lokasi(
    con: duckdb.DuckDBPyConnection,
    n: int = 10
) -> pl.DataFrame:
    """Menghitung jumlah lowongan berdasarkan negara."""

    _register_parquet(con)

    sql = f"""
        SELECT
            search_country AS negara,
            COUNT(*) AS total_lowongan,
            ROUND(
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
                2
            ) AS persentase
        FROM postings
        WHERE search_country != 'Unknown'
        GROUP BY search_country
        ORDER BY total_lowongan DESC
        LIMIT {int(n)};
    """

    return _execute_to_polars(con, sql)


def query_tren_lowongan(
    con: duckdb.DuckDBPyConnection
) -> pl.DataFrame:
    """Menghitung tren jumlah lowongan berdasarkan tanggal."""

    _register_parquet(con)

    sql = """
        SELECT
            first_seen AS periode,
            COUNT(*) AS total_lowongan
        FROM postings
        WHERE first_seen IS NOT NULL
        GROUP BY first_seen
        ORDER BY periode ASC;
    """

    return _execute_to_polars(con, sql)


def query_distribusi_job_type(
    con: duckdb.DuckDBPyConnection
) -> pl.DataFrame:
    """Menghitung distribusi jenis pekerjaan."""

    _register_parquet(con)

    sql = """
        SELECT
            job_type,
            COUNT(*) AS total_lowongan,
            ROUND(
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
                2
            ) AS persentase
        FROM postings
        WHERE job_type != 'Unknown'
        GROUP BY job_type
        ORDER BY total_lowongan DESC;
    """

    return _execute_to_polars(con, sql)


def query_top_perusahaan(
    con: duckdb.DuckDBPyConnection,
    n: int = 10
) -> pl.DataFrame:
    """Mengambil perusahaan dengan jumlah lowongan terbanyak."""

    _register_parquet(con)

    sql = f"""
        SELECT
            company,
            COUNT(*) AS total_lowongan
        FROM postings
        WHERE company != 'Unknown'
        GROUP BY company
        ORDER BY total_lowongan DESC
        LIMIT {int(n)};
    """

    return _execute_to_polars(con, sql)


def query_top_skills(
    con: duckdb.DuckDBPyConnection,
    n: int = 10
) -> pl.DataFrame:
    """Mengambil keterampilan yang paling banyak dibutuhkan."""

    _register_parquet(con)

    sql = f"""
        WITH skill_individual AS (
            SELECT DISTINCT
                job_link,
                TRIM(skill) AS skill
            FROM skills,
            UNNEST(STRING_SPLIT(job_skills, ',')) AS t(skill)
            WHERE TRIM(skill) != ''
        )
        SELECT
            skill,
            COUNT(*) AS total_lowongan
        FROM skill_individual
        GROUP BY skill
        ORDER BY total_lowongan DESC
        LIMIT {int(n)};
    """

    return _execute_to_polars(con, sql)


def hitung_moving_average_polars(
    df: pl.DataFrame,
    col_name: str = "total_lowongan",
    window_size: int = 3
) -> pl.DataFrame:
    """Menghitung rata-rata bergerak menggunakan Polars."""

    if window_size <= 0:
        raise ValueError("window_size harus lebih besar dari 0")

    if col_name not in df.columns:
        raise ValueError(f"Kolom {col_name} tidak ditemukan")

    return df.with_columns(
        pl.col(col_name)
        .rolling_mean(window_size=window_size)
        .round(2)
        .alias(f"ma_{window_size}")
    )



def deteksi_anomali_iqr_polars(
    df: pl.DataFrame,
    col_name: str = "total_lowongan",
    multiplier: float = 1.5
) -> pl.DataFrame:
    """Mendeteksi pencilan menggunakan metode Interquartile Range."""

    if col_name not in df.columns:
        raise ValueError(f"Kolom {col_name} tidak ditemukan")

    if multiplier <= 0:
        raise ValueError("multiplier harus lebih besar dari 0")

    q1 = df[col_name].quantile(0.25)
    q3 = df[col_name].quantile(0.75)

    iqr = q3 - q1
    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)

    return df.with_columns(
        (
            (pl.col(col_name) < lower_bound)
            | (pl.col(col_name) > upper_bound)
        ).alias("is_outlier")
    )

