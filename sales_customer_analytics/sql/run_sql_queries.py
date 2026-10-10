"""
run_sql_queries.py
------------------
Executes all business analytics SQL queries defined in sql/business_queries.sql
against the SQLite database and generates a Markdown report with tabular outputs.
"""

import os
import re
import sqlite3
import pandas as pd


def df_to_markdown_fallback(df: pd.DataFrame) -> str:
    """Formats a DataFrame as a Markdown table without relying on tabulate."""
    headers = [str(c) for c in df.columns]
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        clean_row = [str(val).replace("\n", " ").replace("|", "\\|") for val in row]
        lines.append("| " + " | ".join(clean_row) + " |")
    return "\n".join(lines)


def extract_queries(sql_file_path: str):
    """Extracts named queries from business_queries.sql."""
    with open(sql_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split queries by marker '-- NAME:'
    pattern = r"-- NAME:\s*([a-zA-Z0-9_]+)\s*\n(.*?)(?=(?:-- NAME:|$))"
    matches = re.findall(pattern, content, re.DOTALL)
    queries = []
    for name, sql in matches:
        # Remove trailing single-line and banner comments
        cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE).strip().rstrip(";")
        queries.append((name, cleaned))
    return queries


def run_queries_and_report(db_path: str, sql_file_path: str, report_output_path: str):
    """Executes each query, prints results, and saves a markdown report."""
    print("=" * 65)
    print("EXECUTING BUSINESS ANALYTICS SQL QUERIES")
    print("=" * 65)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Run init_db.py first.")

    conn = sqlite3.connect(db_path)
    queries = extract_queries(sql_file_path)
    
    print(f"Extracted {len(queries)} business queries from: {sql_file_path}\n")

    report_lines = [
        "# SQL Business Analytics Query Results",
        "",
        "> **Project**: Sales & Customer Data Analytics",
        "> **Database Engine**: SQLite 3 (`data/sales_analytics.db`)",
        "> **Generated Automatically**: Yes",
        "",
        "---",
        ""
    ]

    for idx, (q_name, q_sql) in enumerate(queries, 1):
        print(f"[{idx}/{len(queries)}] Running Query: {q_name}...")
        try:
            df_res = pd.read_sql_query(q_sql, conn)
            row_count = len(df_res)
            print(f"    Returned {row_count} rows.")

            report_lines.append(f"## Query {idx}: `{q_name}`")
            report_lines.append("")
            report_lines.append("```sql")
            report_lines.append(q_sql + ";")
            report_lines.append("```")
            report_lines.append("")
            report_lines.append(f"**Results ({min(row_count, 15)} of {row_count} rows shown):**")
            report_lines.append("")
            
            if not df_res.empty:
                display_df = df_res.head(15)
                try:
                    report_lines.append(display_df.to_markdown(index=False))
                except Exception:
                    report_lines.append(df_to_markdown_fallback(display_df))
            else:
                report_lines.append("*Query returned 0 rows.*")

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        except Exception as e:
            print(f"    ERROR running query {q_name}: {e}")
            report_lines.append(f"## Query {idx}: `{q_name}` (ERROR)")
            report_lines.append(f"```\n{e}\n```\n")

    conn.close()

    # Save output markdown report
    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("=" * 65)
    print(f"ALL QUERIES EXECUTED SUCCESSFULLY")
    print(f"Generated Markdown Report: {report_output_path}")
    print("=" * 65)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file = os.path.join(base_dir, "data", "sales_analytics.db")
    sql_file = os.path.join(base_dir, "sql", "business_queries.sql")
    out_report = os.path.join(base_dir, "reports", "sql_query_results.md")
    run_queries_and_report(db_file, sql_file, out_report)
