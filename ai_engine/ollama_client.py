import ollama


def generate_explanation(data):

    formatted = "\n".join(
        [f"{d['parameter']} = {d['value']} ({d['status']})" for d in data]
    )

    prompt = f"""
You are a clinical laboratory analysis assistant.

Patient lab results:

{formatted}

Tasks:
1. Identify abnormal parameters
2. Explain possible medical significance
3. Avoid making definitive diagnoses
4. Suggest follow-up tests
"""

    response = ollama.chat(

        model="llama3",

        messages=[
            {"role": "user", "content": prompt}
        ]

    )

    return response["message"]["content"]