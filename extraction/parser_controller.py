from extraction.dynamic_parser import parse_text_results
from extraction.table_parser import parse_table_results


def parse_report(text, tables=None):
    """
    Master parser controller
    Decides whether to parse tables or raw text
    """

    results = []

    # Try table parsing first
    if tables:
        results = parse_table_results(tables)

    # Fallback to text parsing
    if not results:
        results = parse_text_results(text)

    return results