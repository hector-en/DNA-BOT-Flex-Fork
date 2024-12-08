import openai

def generate_optimized_code(template, diff_log, insights):
    """
    Use GPT or SPINN API to generate optimized Python code.
    Args:
        template: Original Python protocol.
        diff_log: List of diffs applied to the template.
        insights: Mapping matrix insights.
    Returns:
        optimized_code: AI-generated Python code.
    """
    prompt = (
        "You are an AI specializing in optimizing biological workflows. "
        "Below is the original template, diffs applied, and a mapping of experimental results. "
        "Generate an optimized Python protocol to improve the Z-factor while minimizing pipetting steps.\n\n"
        f"Original Template:\n{template}\n\n"
        f"Diff Log:\n{diff_log}\n\n"
        f"Mapping Insights:\n{insights}\n\n"
        "Optimized Protocol:"
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1500,
    )
    return response["choices"][0]["text"]
