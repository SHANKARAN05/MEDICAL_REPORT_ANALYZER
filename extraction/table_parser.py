def parse_table_results(tables):

    results = []

    for table in tables:

        for row in table:

            if len(row) >= 2:

                parameter = str(row[0]).strip()
                value = str(row[1]).strip()

                try:
                    value = float(value)

                    results.append({
                        "parameter": parameter,
                        "value": value
                    })

                except:
                    continue

    return results