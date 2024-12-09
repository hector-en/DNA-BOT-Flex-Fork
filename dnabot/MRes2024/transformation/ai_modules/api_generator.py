import openai
import json
#import yaml

def generate_optimized_code(template_code, diffs, insights, mapping_matrix, api_key, api_engine="gpt-4"):
    """
    Generate optimized Python protocol using AI API.
    Args:
        template_code (str): Original protocol template code.
        diffs (list): List of diff lines.
        insights (dict): Experimental insights (e.g., Z-factor predictions, missing components).
        mapping_matrix (dict): Mapping matrix correlating diffs and experimental results.
        api_key (str): API key for the AI model.
        api_engine (str): AI engine to use (default: "gpt-4").
    Returns:
        tuple: Optimized protocol (str) and inferred insights (dict).
    """
    try:
        print("[INFO] Sending request to AI API for optimized protocol generation...")

        # Construct the prompt
        prompt = (
            "You are an AI specializing in optimizing Opentrons protocols for synthetic biology workflows.\n"
            "Based on the provided template code, diff log, mapping matrix, and experimental insights, "
            "generate an optimized Python protocol. Additionally, infer a set of experimental parameters or "
            "improvements to enhance protocol performance.\n\n"
            f"Template Code:\n{template_code}\n\n"
            f"Diff Log:\n{''.join(diffs)}\n\n"
            f"Experimental Insights:\n{json.dumps(insights, indent=4)}\n\n"
            f"Mapping Matrix:\n{json.dumps(mapping_matrix, indent=4)}\n\n"
            "Please return the results in the following format:\n"
            "Optimized Protocol:\n"
            "[Your Python code here]\n\n"
            "Inferred Insights:\n"
            "[Your JSON-formatted insights here]"
        )

        # Call the OpenAI API
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=api_engine,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )

        # Extract optimized protocol and inferred insights
        response_content = response["choices"][0]["message"]["content"]
        optimized_protocol, inferred_insights = parse_response(response_content)
        
        # Save the inferred insights to a JSON file
        insights_path = LOG_DIR / f"inferred_insights_{reaction}_{original_name}_{TIMESTAMP}.json"
        with open(insights_path, "w") as insights_file:
            json.dump(inferred_insights, insights_file, indent=4)
        print(f"[INFO] Inferred insights saved to {insights_path}")
        
        print("[INFO] Optimized protocol successfully generated.")
        return optimized_protocol, inferred_insights
    except Exception as e:
        print(f"[ERROR] Failed to generate optimized code: {e}")
        return "", {}

def parse_response(response_content):
    """
    Parse the AI API response to extract the optimized protocol and inferred insights.
    Args:
        response_content (str): Response from the API.
    Returns:
        tuple: Optimized protocol (str) and inferred insights (dict).
    """
    try:
        # Split the response into protocol and insights sections
        sections = response_content.split("Inferred Insights:")
        optimized_protocol = sections[0].replace("Optimized Protocol:", "").strip()
        inferred_insights = json.loads(sections[1].strip())
        return optimized_protocol, inferred_insights
    except Exception as e:
        print(f"[ERROR] Failed to parse API response: {e}")
        return "", {}

def save_protocol(optimized_code, output_file):
    """
    Save the optimized Python protocol to a file.
    Args:
        optimized_code (str): Python code for the optimized protocol.
        output_file (str or Path): Path to save the protocol.
    """
    try:
        with open(output_file, "w") as f:
            f.write(optimized_code)
        print(f"[INFO] Optimized protocol saved to {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to save optimized protocol: {e}")

def save_yaml_configuration(
    optimized_code, insights, mapping_matrix, diffs, previous_yaml, output_file, api_key, api_engine="gpt-4"
):
    """
    Generate and save a comprehensive YAML configuration file for the optimized protocol.
    Args:
        optimized_code (str): Python code for the optimized protocol.
        insights (dict): Experimental insights (e.g., Z-factor, efficiency).
        mapping_matrix (dict): Mapping matrix correlating diffs and experimental results.
        diffs (list): List of diff lines.
        previous_yaml (str or Path): Path to the reference YAML file.
        output_file (str or Path): Path to save the YAML configuration.
        api_key (str): API key for GPT.
        api_engine (str): GPT model to use (default: "gpt-4").
    """
    try:
        print("[INFO] Generating comprehensive YAML configuration using GPT...")

        # Read the reference YAML file
        with open(previous_yaml, "r") as f:
            reference_yaml = f.read()

        # Construct the prompt
        prompt = (
            "You are an AI specializing in synthetic biology protocol optimization.\n"
            "Using the following inputs, generate a YAML configuration that aligns with the optimized Python protocol:\n"
            "- Metadata (e.g., protocol name, description, apiLevel).\n"
            "- Calibration parameters (e.g., Z-factor thresholds, pipetting accuracy).\n"
            "- Deck setup (e.g., labware, slots).\n"
            "- Included are ML-inferred insights, mapping matrix correlations, and diff log context.\n\n"
            f"Optimized Code:\n{optimized_code}\n\n"
            f"Experimental Insights:\n{json.dumps(insights, indent=4)}\n\n"
            f"Mapping Matrix:\n{json.dumps(mapping_matrix, indent=4)}\n\n"
            f"Diff Log:\n{''.join(diffs)}\n\n"
            f"Reference YAML:\n{reference_yaml}\n\n"
            "Please return the YAML content only, formatted appropriately."
        )

        # Call GPT API
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=api_engine,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7
        )

        # Extract YAML content from the response
        yaml_content = response["choices"][0]["message"]["content"]

        # Save YAML content to file
        with open(output_file, "w") as f:
            f.write(yaml_content)
        print(f"[INFO] YAML configuration saved to {output_file}")

    except Exception as e:
        print(f"[ERROR] Failed to generate YAML configuration: {e}")
