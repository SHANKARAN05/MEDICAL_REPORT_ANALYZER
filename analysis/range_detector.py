import re

def parse_range(range_text):

    if not range_text:
        return None, None

    numbers = re.findall(r'\d+\.?\d*', range_text)

    if len(numbers) >= 2:
        low = float(numbers[0])
        high = float(numbers[1])
        return low, high

    return None, None