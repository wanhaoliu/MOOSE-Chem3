import json
import ast
from typing import List, Dict, Tuple
import requests
import json
import re
import os
from gpt_api import api_request
import random

# def generate_key_point_prompt(research_question: str, hypotheses: List[Tuple[str, str]]) -> str:
#     """
#     Generates the prompt for clustering based on the research question, hypotheses, and categories.
#     """
#     prompt = f"""
#     We are working on the scientific problem: {research_question}
#     You are an experienced chemistry expert. Below, I will provide you with scientific hypothesis. Please identify the chemical key points that constitute the hypothesis, chemical key points are the core key elements for effectively solving the scientific problem. The analysis of chemical key points needs to be combined with specific scientific problem for consideration, identifying which key points in the scientific hypothesis can solve these problems. When identifying chemical key points, note that each substance may be a chemical key point. Please carefully analyze and judge. At the same time, if multiple substances exist and are related, such as potassium ferricyanide and potassium ferrocyanide, they are a pair of oxidizing and reducing substances. Therefore, such a pair of substances belongs to one chemical key point. The basis for classification is that they have the same function or need to exist together to work. These chemicals should be considered as one key point. Additionally, identify the results—effects or phenomena caused by these chemical key points. These represent the achievements or effects of the experiment. Note that the results are the effects or phenomena caused by these chemical key points, so when performing the output, pay attention to outputting the chemical key points, not the results. At the same time, you need to pay attention that the scientific hypothesis to be analyzed will contain validation methods for the experiment, such as using elemental analysis to verify the properties of a certain substance, etc. These are validations of the scientific hypothesis, not scientific key points. Scientific key points are the core key  elements for effectively solving the scientific problem, not the validation methods. When identifying the key points in the hypothesis, it's important to combine them with the scientific problem. For example, if the scientific problem is about how to improve the mechanical properties of MXene nanosheets, then the MXene nanosheets mentioned in the hypothesis as being enhanced by the addition of liquid metal should be considered as a prerequisite, not a chemical key point. In this case, the liquid metal would be the chemical key point. Before output, please check whether the chemical key point includes the substance in the scientific problem. If it does, please remove it. Based on the results, analyze the role and function of each chemical substance or method. Use your chemical knowledge to provide detailed descriptions. When analyzing the role and function of each chemical substance or method based on the results, it is also important to relate it to the chemical question. Think about how the characteristics of the chemical key points address and solve the chemical problem. You need to combine your chemical knowledge to provide a detailed explanation of the specific mechanisms of each chemical key point, as well as the connections between these key points. When identifying the Chemical Key Points, be mindful that elements mentioned in the scientific question that appear in the scientific hypothesis are not considered Chemical Key Points, but rather prerequisites.The prerequisites should not be analyzed or outputted.
#     Output format:
#     ###Chemical Key Points###
#     Chemical substance/component/method 1
#     Role and Function: Describe the role and function of the substance or method.
#     Chemical substance/component/method 2
#     Role and Function: Describe the role and function of the substance or method.
#     ###End Chemical Key Points###

#     ###Results###
#     Result 1:
#     Describe the effects caused by the aforementioned reasons (e.g., performance improvement, efficiency changes).
#     Result 2:
#     Further describe other effects related to the experimental objectives.
#     ###End Results###
#     Example:
#     ###Chemical Key Points###
#     1.PVA (Polyvinyl Alcohol)
#     Role and Function: Polyvinyl alcohol (PVA) hydrogel acts as the base material, providing structural support and mechanical performance for thermoelectric gels.
#     2.Gdm₂SO₄ (Guanidine Sulfate)
#     Role and Function: Guanidine sulfate (Gdm₂SO₄) is integrated into the PVA hydrogel to improve thermoelectric performance. The introduction of guanidine salt increases solvent entropy and effectively enhances thermopower.
#     3.Directional Freezing Method
#     Role and Function: By employing directional freezing technology, aligned channels are created, enhancing the electrical conductivity and mechanical strength of the material.
#     4.Potassium Ferricyanide and Potassium Ferrocyanide (K₃[Fe(CN)₆] / K₄[Fe(CN)₆])
#     Role and Function: These compounds are crucial electrolytes that facilitate redox reactions within the polymer gel. The presence of these ions enhances ion mobility and conductivity due to their ability to undergo reversible redox processes, thereby boosting the thermoelectric properties of the gel
#     ###End Chemical Key Points###
#     ###Results###
#     Carnot-relative Efficiency
#     The Carnot-relative efficiency of the FTGA exceeds 8%.
#     Thermopower and Mechanical Robustness
#     Thermopower and mechanical robustness are enhanced, outperforming traditional quasi-solid-state thermoelectric cells.
#     ###End Results###
#     Please analyze below.hypotheses is {hypotheses}"""
#     return prompt


# def extract_gene_hypothesis(feedback):
#     match = re.search(r"(###Chemical Key Points###.*?###End Chemical Key Points###)", feedback,re.DOTALL)
#     return match.group(1).strip() if match else None
# def get_gene_hypothesis_with_retry(prompt, api_request):
#     """
#     Tries to extract Ground Truth Scientific Hypothesis Key with retries.

#     Args:
#         pro_prompt (str): The initial prompt for the API request.
#         cur_gdth_hyp (str): The current Ground Truth Hypothesis.
#         api_request (callable): Function to make an API request.
#         max_retries (int): The maximum number of retries if extraction fails.

#     Returns:
#         str: Extracted Ground Truth Hypothesis Key or None if retries exhausted.
#     """
#     retry_count = 0
#     max_retries = 5
#     while retry_count < max_retries:
#         # Construct the full prompt by adding the current hypothesis
#         feedback = api_request(prompt)
#         print(f"\n\nfeedback\n{feedback}")
#         # Extract the score       
#         gene_hypothesis_chem_key = extract_gene_hypothesis(feedback)
#         if  gene_hypothesis_chem_key is not None:
#             return gene_hypothesis_chem_key
#         else:
#             print("Error: Failed to extract valid Gene Hypothesis Key. Retrying...")
#             prompt += """Please strictly follow the output format below. It must include ###Chemical Key Points###, ###End Chemical Key Points###, ###Results###, and ###End Results###. The output format is:###Chemical Key Points###Chemical substance/component/method  Role and Function: Describe the role and function of the substance or method.###End Chemical Key Points###\n###Results###Result:Describe the effects caused by the aforementioned reasons (e.g., performance improvement, efficiency changes).###End Results###"""
#             retry_count += 1

#     # If the maximum retry limit is reached and extraction failed, return None
#     print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")
#     return None

# gene_hypothesis_chem_key = get_gene_hypothesis_with_retry(prompt, api_request)
# Set the Base URL and API key for your custom API
# Baseurl = "https://api.claudeshop.top"
# Skey = "sk-svowCeqZw45Y7t1GJnuiOw5v9Rg9btsqWbPEa9IBSshZj4bm"

# # Function to make API requests
# def api_request(messages):
#     url = Baseurl + "/v1/chat/completions"
#     headers = {
#         'Accept': 'application/json',
#         'Authorization': f'Bearer {Skey}',
#         'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
#         'Content-Type': 'application/json'
#     }
#     payload = json.dumps({
#         "model": "gpt-4o-2024-08-06",
#         # "messages": messages
#         "messages": [{"role": "system", "content": "You are a helpful assistant."},
#                      {"role": "user", "content": messages}]
#     })
    
#     response = requests.post(url, headers=headers, data=payload)
    
#     if response.status_code == 200:
#         return response.json()["choices"][0]["message"]["content"].strip()
#     else:
#         raise Exception(f"API request failed with status {response.status_code}: {response.text}")

# Function to generate verifier's hypothesis
# def gpt(prompt):
#     hypothesis = api_request(prompt)
#     return hypothesis

def extract_effective_category(feedback):
    """
    Extract the dictionary between ###Category Assignment### and ###END Category Assignment###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        dict: Extracted dictionary or None if the pattern is not found.
    """
    # Regex to match content between ###Category Assignment### and ###END Category Assignment###
    match = re.search(r"###\s*Effective Categories\s*###\s*(.*?)\s*###\s*End\s*###", feedback, re.DOTALL)
    if match:
        content = match.group(1).strip()
        try:
            # Convert the content to a dictionary using `ast.literal_eval`
            return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            # If parsing fails, return None
            return None
    return None

def extract_scientific_hypothesis(feedback):
    """
    Extract the dictionary between ###Scientific Hypothesis### and ###END Scientific Hypothesis###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        dict: Extracted dictionary or None if the pattern is not found.
    """
    # Regex to match content between ###Scientific Hypothesis### and ###END Scientific Hypothesis###
    match = re.search(r"###\s*Scientific\s*Hypothesis\s*###\s*(.*?)\s*###\s*End\s*###", feedback, re.DOTALL)
    if match:
        content = match.group(1).strip()
        try:
            # Convert the content to a dictionary using `ast.literal_eval`
            return ast.literal_eval(content.replace("\n","  "))
            # return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            # If parsing fails, return None
            return None
    return None

def extract_advice_list(text):
    advice_pattern = r"###\s*Advice\s*###\s*(.*?)\s*###\s*End\s*###"
    effective_pattern = r"###\s*Effective\s*Categories\s*###\s*(.*?)\s*###\s*End\s*###"
    advice_match = re.search(advice_pattern, text, re.DOTALL | re.IGNORECASE)
    effective_match = re.search(effective_pattern, text, re.DOTALL)
    advice_content = advice_match.group(1).strip() if advice_match else None
    effective_categories = None
    if effective_match:
        content = effective_match.group(1).strip()
        try:
            effective_categories = ast.literal_eval(content)
        except (ValueError, SyntaxError):
            effective_categories = None

    return advice_content, effective_categories


def extract_advice(feedback):
    """
    Extract the content between ###Advice### and ###End###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        str: Extracted advice or None if the pattern is not found.
    """
    # Regex to match content between ###Advice### and ###End###
    # match = re.search(r"###Advice###\s*(.*?)\s*###End###", feedback, re.DOTALL)
    match = re.search(r"###\s*Advice\s*###\s*(.*?)\s*###\s*End\s*###", feedback,re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()  # Extract and return the advice content
    return None

def read_research_question(filepath: str, sub_index: int) -> str:
    """
    Reads the research question from the JSON file based on the sub_index.
    """
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)

    if sub_index < len(data[0]):
        return data[0][sub_index]
    else:
        raise IndexError("sub_index exceeds the number of available research questions.")

# def choose_category_prompt(research_question: str,  existing_categories: List[str]) -> str:
#     """
#     Generates the prompt for clustering based on the research question, hypotheses, and categories.
#     """
#     prompt = f"""
#     You are a chemistry expert tasked with addressing the chemical question: {research_question} I will provide you with chemical categories relevant to solving this problem, and you need to analyze and identify which categories are the most effective for addressing this challenge. The chemical categories name that most effectively addresses this challenge is Effective Categories.The output format must strictly adhere to the provided category names. The Effective Categories must be in list format, and the list cannot contain more than 3 elements.    
#     Below are the chemical categories.\n{existing_categories}
#     For example, consider the question of improving the electrical performance of thermoelectric materials. First, analyze the question: what aspects are included in electrical performance (e.g., electrical conductivity, resistance)? Then, consider the properties of thermoelectric materials. For instance, polymers as thermoelectric materials can utilize their specific characteristics, such as freeze-polymerization, to construct freeze-oriented structures. Upon analysis, freeze-oriented ion channels can reduce resistance and enhance conductivity, achieving improved electrical performance. Consequently, freeze-polymerization or oriented crystallization would align with categories relevant to these classifications and should be selected in the output.The categories must be in list format, and the list cannot contain more than 3 elements.Please note that Effective Categories selection should be strictly from the chemical categories. Please verify the output format.The output format is as follows
#     ###Effective Categories###
#     ["Category Name Chosen from chemical categories"]
#     ###End###\n
    
#     """
#     return prompt

#and the list cannot contain more than 3 elements

def choose_category_prompt(research_question: str,  existing_categories: List[str]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    You are a chemistry expert tasked with addressing the chemical question: {research_question} I will provide you with chemical categories relevant to solving this problem, and you need to analyze and identify which categories are the most effective for addressing this challenge. The chemical categories name that most effectively addresses this challenge is Effective Categories.The output format must strictly adhere to the provided category names. The Effective Categories must be in list format, and the list can only contain one element.    
    Below are the chemical categories.\n{existing_categories}
    For example, Let’s think step by step, consider the question of improving the electrical performance of thermoelectric materials. First, analyze the question: what aspects are included in electrical performance (e.g., electrical conductivity, resistance)? Then, consider the properties of thermoelectric materials. For instance, polymers as thermoelectric materials can utilize their specific characteristics, such as freeze-polymerization, to construct freeze-oriented structures. Upon analysis, freeze-oriented ion channels can reduce resistance and enhance conductivity, achieving improved electrical performance. Consequently, freeze-polymerization or oriented crystallization would align with categories relevant to these classifications and should be selected in the output.The categories must be in list format, and the list can only contain one element.Please note that Effective Categories selection should be strictly from the chemical categories. Please verify the output format.The output format is as follows
    ###The Thinking Process###
    ###Effective Categories###
    ["Category Name Chosen from chemical categories"]
    ###End###\n
    """
    return prompt
# explore
def choose_hypothesis_prompt(research_question: str,  effective_categories: List[str], cur_category: str, hypotheses: List[Tuple[str, str]]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    You are a chemistry expert tasked with analyzing the chemical question: {research_question} You currently identify effective chemical categories {effective_categories} and analyze the {cur_category} category. The scientific hypotheses contained within this category are {hypotheses}. Select the scientific hypothesis that you believe best addresses the problem through analysis. 
    If the effective chemical categories contain only one category, please analyze and select the hypothesis that you believe best addresses the chemical question.
    If the effective chemical categories contain more than one category. Please select the hypothesis that best represents the characteristics of this category while distinguishing it from other effective chemical categories.For example, if the chemical question is How can we improve the electrical performance of thermoelectric materials? and the effective chemical categories are {{"Freeze-Polymerization Orientation", "Dual-Network Gels","Ionic Liquids"}}, then when selecting a scientific hypothesis for the category "Freeze-Polymerization Orientation," avoid choosing hypotheses that include characteristics of "dual-network structures" (e.g., hypotheses involving constructing the first network structure followed by the second). Ensure the selected hypothesis highlights the unique features of this category.
    Output Format
    ###The Thinking Process###
    ###Scientific Hypothesis###
    {{"Category Name Chosen from Existing Categories":["id of Scientific Hypothesis","Scientific Hypothesis"]}}
    ###End###
        """
    return prompt


def save_to_storage(index, current_dict, existing_categories):
    """
    Save the current state of current_dict and existing_categories.
    
    Args:
        index (int): The current index to be saved.
        current_dict (dict): The dictionary containing category assignments.
        existing_categories (list): The list of existing categories.
    """
    file_path = f"output_{index}.json"
    save_data = {
        "current_dict": current_dict,
        "existing_categories": existing_categories
    }
    with open(file_path, 'w',encoding='utf-8') as f:
        import json
        json.dump(save_data, f, indent=4)
    print(f"Saved data for index {index} to {file_path}")



def process_json_files(base_dir, index):
    """
    Reads a specific JSON file from the given directory and processes it.

    :param base_dir: The directory containing the JSON files.
    :param i: The index of the JSON file to read (e.g., for output_i.json).
    :return: The data from the JSON file if successfully read, else None.
    """
    file_name = f"output_class_{index}.json"
    file_path = os.path.join(base_dir, file_name)

    try:
        # Read and process the specific JSON file
        with open(file_path, 'r',encoding='utf-8') as file:
            data = json.load(file)
            # You can process the `data` as required here
            # print(f"Successfully read {file_name}")
            current_dict = data.get("current_dict", {})
            existing_categories = data.get("existing_categories", None)
            print(f"Successfully read {file_name}")
            return current_dict, existing_categories
            # return data  # Return the data for further processing if needed

    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {file_name}")
    except Exception as e:
        print(f"An error occurred while processing {file_name}: {e}")

    return None  # Return None if an error occurred

def generate_hypotheses(data, index, cur_category, current_dict):
    """
    Generate hypotheses based on effective categories and corresponding values in current_dict.

    Args:
        data_path (str): The file path to read additional data.
        index (int): The index to locate the JSON data file.
        effective_categories (list): List of effective categories.
        current_dict (dict): Dictionary containing category mappings.

    Returns:
        list: A list of hypotheses as tuples of (key, value).
    """
    # Load the external data
    hypotheses = []
     #current_dict {name:[id]}
    if cur_category in current_dict:
        category_values = current_dict[cur_category]  # Get the list of values for the category
        
        for value in category_values:
            # print(value)
            # Safely retrieve the corresponding value from data[0]
            try:
                value_key = str(value)  # Ensure the key is a string
                # print(value_key)
                if value_key in data[1][index]:
                    hypotheses.append((value_key, data[1][index][value_key]))
                    # print(hypotheses)（id,hypo)
            except Exception as e:
                print(f"Error accessing data for key {value_key}: {e}")

    return hypotheses


# def validate_and_retry_categories(feedback, prompt, api_request):
#     """
#     Validates if extracted categories are a list with at most 3 elements. Retries if invalid.

#     Args:
#         feedback (str): The input feedback to extract categories from.
#         prompt (str): The initial prompt used for the API request.
#         api_request (callable): Function to make an API request.

#     Returns:
#         list: Validated list of categories or None if validation fails after retry.
#     """
#     categories = extract_effective_category(feedback)
#     # print( f"category_assignment\n\n{categories}")

#     if not isinstance(categories, list) or len(categories) > 3:
#         print(f"Error: Extracted categories are not a valid list with at most 3 elements. Received: {categories}")
#         print("Retrying API request to ensure valid list output...")
#         prompt += " The categories must be in list format, and the list cannot contain more than 3 elements. Please verify the output format."
#         retry_feedback = api_request(prompt)
#         print(f"Retry feedback:\n\n{retry_feedback}")
#         categories = extract_effective_category(retry_feedback)
        
#         # Validate again after retry
#         if not isinstance(categories, list) or len(categories) > 3:
#             print(f"Critical Error: Retried API request still did not return a valid list. Received: {categories}")
#             print("Skipping current iteration due to invalid data format.")
#             return None
#     return categories

def validate_and_retry_categories(feedback, prompt, api_request,existing_categories):
    """
    Validates if extracted categories are a list with at most 3 elements. Retries if invalid.
    
    Args:
        feedback (str): The input feedback to extract categories from.
        prompt (str): The initial prompt used for the API request.
        api_request (callable): Function to make an API request.
        max_retries (int): The maximum number of retries allowed. Default is 5.
    
    Returns:
        list: Validated list of categories or None if validation fails after retry.
    """
    
    # print(f"category_assignment\n\n{categories}")
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
    # while retry_count < max_retries:
    #     if not isinstance(categories, list) or len(categories) > 3:
            categories = extract_effective_category(feedback)
            if isinstance(categories, list):
                categories = [item.lower() for item in categories]
                if all(category in existing_categories for category in categories):
                    print(f"Successfully validated categories: {categories}")
                    return categories,feedback
                else:
                    not_in_existing_categories = []
                    for category in categories:
                        if category not in existing_categories:
                            not_in_existing_categories.append(category)
                    print(f"Error: Some categories are not in the existing categories. Extracted: {categories},not in existing categories {not_in_existing_categories}")
                    prompt +=f""" Do not directly output the recommended categories. Among them, {not_in_existing_categories} is not in the candidate chemical categories. Please select the categories that are in the candidate chemical categories.You need to identify relevant categories from the candidate chemical categories. Once you've selected them, output the category names correctly and completely from the candidate chemical categories.The output format is as follows###Effective Categories###["Category Name Chosen from chemical categories"]###End###\n
                    """
                    retry_count += 1
                    print(f"Attempt {retry_count} failed. Retrying...")
                    feedback = api_request(prompt)
                    print(f"Retry feedback:\n\n{feedback}")
                    continue
                    
            print(f"Error: Extracted categories are not a valid list. Received: {categories}")
            print(f"Retrying API request to ensure valid list output... Attempt {retry_count + 1}/{max_retries}")
            prompt += """The categories must be in list format, and Please verify the output format,The output format is as follows:###Effective Categories###["Category Name Chosen from chemical categories"]###End###."""
            retry_count += 1
            print(f"Attempt {retry_count} failed. Retrying...")
            feedback = api_request(prompt)
            print(f"Retry feedback:\n\n{feedback}")
            # categories = extract_effective_category(retry_feedback)

            # Check if categories are valid
            
        # If after max_retries we still have invalid categories
    print(f"Critical Error: After {max_retries} attempts, the API request did not return a valid list. Received: {categories}")
    print("Skipping current iteration due to invalid data format.\n" + "\n" * 6)
    random_category = random.choice(existing_categories)
    new_list = [random_category]
    print("New list with one random category:", new_list)
    return new_list,feedback


# def validate_and_retry_hypothesis(feedback, prompt, api_request):
#     """
#     Validates if the extracted scientific hypothesis is a valid dictionary. Retries if invalid.

#     Args:
#         feedback (str): The input feedback to extract the scientific hypothesis from.
#         prompt (str): The initial prompt used for the API request.
#         api_request (callable): Function to make an API request.

#     Returns:
#         dict: Validated scientific hypothesis dictionary or None if validation fails after retry.
#     """
#     # Extract scientific hypothesis using the provided function
#     scientific_hypothesis = extract_scientific_hypothesis(feedback)
#     print(f"Extracted scientific_hypothesis:\n\n{scientific_hypothesis}")

#     # Check if the extracted hypothesis is a valid dictionary
#     if not isinstance(scientific_hypothesis, dict):
#         print(f"Error: Extracted hypothesis is not a valid dictionary. Received: {scientific_hypothesis}")
#         print("Retrying API request to ensure valid dictionary output...")

#         # Modify prompt to reinforce that the output must be in dictionary format
#         prompt += " The scientific hypothesis must be in dictionary format. Please ensure the output format is correct."
        
#         # Retry the API request
#         retry_feedback = api_request(prompt)
#         print(f"Retry feedback:\n\n{retry_feedback}")

#         # Try extracting the hypothesis again after retry
#         scientific_hypothesis = extract_scientific_hypothesis(retry_feedback)
        
#         # Validate again after retry
#         if not isinstance(scientific_hypothesis, dict):
#             print(f"Critical Error: Retried API request still did not return a valid dictionary. Received: {scientific_hypothesis}")
#             print("Skipping current iteration due to invalid data format.")
#             return None

#     return scientific_hypothesis

def validate_and_retry_hypothesis(feedback, prompt, api_request):
    """
    Validates if the extracted scientific hypothesis is a valid dictionary. Retries a specified number of times if invalid.

    Args:
        feedback (str): The input feedback to extract the scientific hypothesis from.
        prompt (str): The initial prompt used for the API request.
        api_request (callable): Function to make an API request.
        max_retries (int): Maximum number of retry attempts to extract a valid hypothesis.

    Returns:
        dict: Validated scientific hypothesis dictionary or None if validation fails after retries.
    """
    # Extract scientific hypothesis using the provided function
    
    # print(f"Extracted scientific_hypothesis:\n\n{scientific_hypothesis}")
    max_retries=10
    # Check if the extracted hypothesis is a valid dictionary
    retry_count = 0
    while retry_count < max_retries:
        scientific_hypothesis = extract_scientific_hypothesis(feedback)
        if isinstance(scientific_hypothesis, dict):
            for key, value in scientific_hypothesis.items():  # Iterate over each pair in the dictionary key-value
                if isinstance(value, list) and len(value) > 0:  # Check if value is a non-empty list
                    # Checks if the first element of the list is a valid id (can be an integer or a number as a string)
                    id_value = value[0]
                    if (isinstance(id_value, int) and id_value >= 0) or (isinstance(id_value, str) and id_value.isdigit() and int(id_value) >= 0):
                        return scientific_hypothesis  # If the condition is met, return the dictionary
                    else:
                        print("Error: Extracted hypothesis is not a valid id of Scientific Hypothesis")
                        prompt += """Please ensure the output format is correct.Output Format:###Scientific Hypothesis###{"Category Name Chosen from Existing Categories":["id of Scientific Hypothesis","Scientific Hypothesis"]} ###End###Note: Make sure to correctly output the "id of Scientific Hypothesis"""
            # return scientific_hypothesis
        print(f"Error: Extracted hypothesis is not a valid dictionary. Received: {scientific_hypothesis}")
        print("Retrying API request to ensure valid dictionary output...")
        # Modify prompt to reinforce that the output must be in dictionary format
        prompt += """The scientific hypothesis must be in dictionary format.Note that the value of the dictionary is a list. Please check. Please ensure the output format is correct.Output Format:###Scientific Hypothesis###{"Category Name Chosen from Existing Categories":["id of Scientific Hypothesis","Scientific Hypothesis"]} ###End###"""
        # Retry the API request
        retry_count += 1
        # Check if we've exhausted the retry attempts
        print(f"Retry attempt {retry_count} of {max_retries}...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")

        # Try extracting the hypothesis again after retry
        # scientific_hypothesis = extract_scientific_hypothesis(retry_feedback)
 
    # If after all retries we still don't have a valid dictionary, return None
    print("Critical Error: Could not extract a valid dictionary after retries.")
    return None

    




def save_hypotheses(result_hypotheses,index,output_dir):
    """
    Save the list of hypotheses to a JSON file.

    Args:
        hypotheses (list): The list of hypotheses to save.
    
    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_output_{index}.json")
    # file_path = f"/hypotheses_output_{index}.json"
    try:
        with open(file_path, 'w',encoding='utf-8') as file:
            json.dump(result_hypotheses, file, indent=4)
        print(f"Hypotheses saved to {file_path}")
        return file_path
    
    except Exception as e:
        print(f"Error saving hypotheses: {e}")
        
def choose_hypothesis_main(filepath,research_question_filepath,data_path,num_iterations,output_dir = "."):
    #data_path is a folder containing classifications and their corresponding IDs.
    # Configuration
    # Load data from file
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)  
        
    for index in range(num_iterations):
        print(f"#########################{index}#############################")
        current_dict, existing_categories = process_json_files(data_path,index)
        research_question = read_research_question(research_question_filepath, index)
        category_prompt = choose_category_prompt (research_question,existing_categories)
        print(category_prompt)
        feedback = api_request(category_prompt)
        print(f"feedback\n\n{feedback}")
        effective_categories = validate_and_retry_categories(feedback,category_prompt, api_request,existing_categories)
        result = []
        for cur_category in effective_categories:
            
            hypotheses = generate_hypotheses (data,index, cur_category, current_dict)
            hypothesis_prompt = choose_hypothesis_prompt(research_question,  effective_categories, cur_category, hypotheses)
            print(f"hypothesis_prompt\n\n{hypothesis_prompt}")
            feedback = api_request(hypothesis_prompt)
            print(f"hypothesis_feedback\n\n{feedback}")
            scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request)
            if scientific_hypothesis:
                result.append(scientific_hypothesis)
            else:
                print(f"Skipping category {cur_category} due to invalid scientific hypothesis format.")
            
        save_hypotheses(result,index,output_dir)
        

    
        
def choose_hypothesis_explore(filepath,research_question_filepath,data_path,index,output_dir = "."):
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)  
    # for index in range(num_iterations):
    print(f"#########################{index}#############################")
    # Read the classified data id and category
    current_dict, existing_categories = process_json_files(data_path,index) 
    research_question = read_research_question(research_question_filepath, index)
    # Recommended experiment categories without prior knowledge
    category_prompt = choose_category_prompt (research_question,existing_categories)
    print(category_prompt)
    feedback = api_request(category_prompt)
    print(f"feedback_category_prompt\n\n{feedback}")
    # Get a list of valid classes
    effective_categories,feedback = validate_and_retry_categories(feedback,category_prompt, api_request,existing_categories)
    result = []
    for cur_category in effective_categories:
        
        hypotheses = generate_hypotheses (data,index, cur_category, current_dict)
        
        hypothesis_prompt = choose_hypothesis_prompt(research_question,  effective_categories, cur_category, hypotheses)
        print(f"hypothesis_prompt\n\n{hypothesis_prompt}")
        feedback = api_request(hypothesis_prompt)
        print(f"hypothesis_feedback\n\n{feedback}")
        scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request)
        if scientific_hypothesis:
            result.append(scientific_hypothesis)
        else:
            print(f"Skipping category {cur_category} due to invalid scientific hypothesis format.")
            
    file_path = save_hypotheses(result,index,output_dir)
    return file_path,result

# def experiment_result_category_advice (score_path, research_question,existing_categories):
#     with open(score_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     experiment_data = data[1]
#     experiment_prompt = ""
#     for i in range(len(experiment_data)):
#         experiment_prompt += f"\nExperiment {i+1}: Category is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]}, Result is {experiment_data[i][5]}\n"
#     prompt = f"""
# You are a chemistry expert tasked with addressing the chemical question: {research_question}. I will provide you with candidate chemical categories  relevant to solving this problem, and you need to give suggestions on the next steps for choosing candidate chemical categories that could lead to better experimental feedback scores, based on existing experimental results, combining your thoughts and extensive chemical knowledge. Below are the candidate chemical categories.\n{existing_categories}\n
# Currently, we have obtained some experimental results. Since there are many scientific hypotheses within each category, we select scientific hypotheses from different categories for experimentation. I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. A score of 0.028 generally covers some of the key points. A single chemical category (or chemical point) cannot be tested in isolation; experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple chemical categories. Therefore, it is important to note that the experimental feedback score is the result of the combined effects of multiple chemical categories, not the result of a single chemical category. The following are the experimental results.\n {experiment_prompt}\n
# Let’s think step by step.When formulating your suggestions, first analyze the research question to clarify the experimental objectives. Identify the key factors that contribute to the ultimate goal of the experiment. Then, break down the experimental hypothesis into chemical key points and determine which chemical categories each element belongs to. Next, in light of the experimental goals, think about which combinations of chemical categories effectively address the objectives of the experiment. Focus on understanding the mechanisms through which these categories work effectively. Evaluate the contribution of each specific chemical category to the overall result. Please specify the percentage of contribution. Finally, reflect on your chemical knowledge, consider the existing experimental scores, and assess whether the mechanisms of action for each chemical category are correct in terms of achieving the experimental goals. Based on this analysis, provide clear recommendations from the candidate chemical categories for the next step, aiming to achieve better experimental feedback.Please note that the experimental feedback structure is arranged from high to low scores. After analyzing the scientific hypotheses with high feedback scores, it is equally important to examine the experimental feedback with low scores. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not achieve the expected results. These insights offer guidance on what to avoid in future hypotheses, effectively recommending steering clear of certain interfering or incorrect chemical points, thereby providing better guidance for selection.
# For example, the chemical question: How can we improve the electrical performance of thermoelectric materials? First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials. What aspects are included in electrical performance (e.g., electrical conductivity, resistance)? Electrical conductivity: This is one of the core aspects of thermoelectric performance, which is usually related to the material's electronic structure and carrier concentration.Resistance: Lowering the resistance can improve the flow of current, thus enhancing the overall electrical performance of the material. Then, break down the experimental hypothesis into chemical key points and determine which chemical categories each element belongs to.Please note that the experimental feedback structure is arranged from high to low scores. Each experimental hypothesis contains multiple scientific key points. For hypotheses with high experimental scores, the feedback recommends which key points should be included in future selections. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not work as expected. These insights offer guidance on what to avoid in future hypotheses and clearly specify which key points should be included next time.
# For example,Let’s think step by step. the scientific hypothesis is to construct ion channels through freeze orientation, polymerize using polyvinyl alcohol (PVA), and add guanidine sulfate to synthesize a gel with good electrical performance. The experimental result is 0.8. Hypothesis breakdown and chemical key points:\nFreeze orientation: This technique is often used to create materials with a directional structure, which could enhance ionic conductivity. This hypothesis falls under the categories of Ion Channels and Material Structure Design. \nPVA polymerization: Polyvinyl alcohol, as a polymer material, affects the material’s electrical conductivity based on its structure and crosslinking degree. PVA polymerization falls under Polymer Design and Crosslink Density categories.\n Guanidine sulfate: As a chemical reagent, guanidine sulfate may be involved in ion exchange or improving conductivity, falling under the Ion Exchange category.\nTo effectively solve the experimental goal, the focus should be on combinations of chemical categories that can impact electrical conductivity and resistance. By thinking through the effective mechanisms, the following chemical category combinations are worth focusing on:\nIon Channels: The structure and alignment of ion channels directly affect the material’s ionic conductivity, with key factors being the directionality of the ion channels. Freeze orientation technology could enhance conductivity by constructing aligned ion channels. \nContributions of the chemical categories to the overall result:\n Ion Channels: Creating ordered ion channels through freeze orientation can reduce resistance, enhance ionic conductivity, and thus improve electrical performance. Potential contribution: 50%\n Polymer Design: Optimizing the crosslink density and molecular structure of the polymer helps to enhance the mechanical strength and stability of thermoelectric materials, indirectly improving electrical performance. Potential contribution: 30% \nIon Exchange: Guanidine sulfate may help improve ionic conductivity, adjusting the carrier concentration and further optimizing the electrical conductivity. Potential contribution: 20% \nEvaluation and Suggestions:The experimental result score of 0.8 indicates that some key points in the hypothesis are effective, with Ion Channels contributing significantly. Therefore, it is highly recommended to prioritize Ion Channels.Please note that the experimental feedback structure is arranged from high to low scores. After analyzing the scientific hypotheses with high feedback scores, it is equally important to examine the experimental feedback with low scores.For example, the hypothesis of improving gel conductivity and thermoelectric performance by adding heavy metals received an experimental feedback score of 0.0000065.  First, break down the key scientific points, which mention heavy metals and conductive gels. By analyzing the experimental results, the low scores indicate that the key points in the hypothesis are not recommended. Comparing the similarities and differences with higher-scoring scientific hypotheses can help explain the underlying mechanisms. For instance, the mechanism of ion channels may contribute to the electrical performance of gels, whereas the mechanism relying on metal conductivity to enhance material performance may have issues. Therefore, it is recommended to avoid approaches that depend on metal conductivity to improve performance.Each experimental hypothesis contains multiple scientific key points. For hypotheses with high experimental scores, the feedback recommends which key points should be included in future selections. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not work as expected. These insights offer guidance on what to avoid in future hypotheses and clearly specify which key points should be included next time.Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than three.Based on the current experimental feedback and my chemical knowledge, here are the recommendations for the next step in the experiment:
# ###Advice###
# Suggested chemical categories to select:
# Ion Channels. Reason: The directional arrangement of ion channels is crucial for enhancing electrical conductivity. Freeze orientation technology is an effective method to create directional ion channels, which can directly influence the material's electrical performance. Strongly recommended to choose Ion Channels.
# Polymer Design Reason: Polyvinyl alcohol (PVA), as a polymer, plays a crucial role in adjusting the stability and conductivity of thermoelectric materials. Optimizing the crosslink density of PVA can effectively enhance the material's electrical performance. Consider selecting Polymer Design.
# It is recommended to avoid including certain chemical categories (the recommended chemical categories should not include them).
# By analyzing the low-scoring experiments, it is concluded that heavy metal components should not be included, as the scientific hypotheses containing heavy metals tend to have lower feedback scores. The analysis suggests this is due to environmental concerns and the limitations they impose on potential applications.The addition of heavy metals may disrupt the existing structure of the gel, leading to a decline in performance.Therefore, it is suggested that the mechanism relying on metal conductivity to enhance material performance may have issues, and it is recommended to avoid options containing these elements.
# ###End###The given advice should not be specific to the class. Instead, it should be summarized based on your understanding of the experimental feedback. Note that the key points to avoid should be based on the understanding of the experimental feedback, and specific suggestions regarding directions do not need to be detailed with numerical values.
# Please note that the suggestions provided should include the complete and correct names of the candidate chemical categories if they are recommended for selection. Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than three. Please analyze based on the key points of the scientific hypotheses derived from experimental feedback. Please note that before your final recommendation, add ###Advice###, and after the recommendation is completed, add ###End###.You need to provide expert recommendations to ensure that the chemical categories chosen for the experiments will yield better results.Output format should strictly follow:
# ###Advice### Suggestions based on experimental feedback ###End### Please think step by step and answer according to the requirements.
#         """
#     return prompt


# def extract_summary_analysis(feedback):
#     """
#     Extract the content between ###Analysis and Summary### and ###End###.

#     Args:
#         feedback (str): The input text to search within.

#     Returns:
#         str: Extracted analysis and summary or None if the pattern is not found.
#     """
#     # Regex to match content between ###Analysis and Summary### and ###End###
#     match = re.search(r"###\s*Analysis\s+and\s+Summary\s*###\s*(.*?)\s*###\s*End\s*###", feedback, re.IGNORECASE | re.DOTALL)
    
#     if match:
#         return match.group(1).strip()  # Extract and return the analysis and summary content
#     return None
def extract_summary_analysis(feedback):
    """
    Extract the content between ###Analysis### and ###End Analysis###, 
    as well as between ###Summary### and ###End Summary###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        tuple: A tuple containing the extracted analysis and summary content. 
               Returns (None, None) if the patterns are not found.
    """
    # Regex to match content between ###Analysis### and ###End Analysis###
    analysis_pattern = r"###\s*Analysis\s*###\s*(.*?)\s*###\s*End\s+Analysis\s*###"
    summary_pattern = r"###\s*Summary\s*###\s*(.*?)\s*###\s*End\s+Summary\s*###"
    
    analysis_match = re.search(analysis_pattern, feedback, re.IGNORECASE | re.DOTALL)
    summary_match = re.search(summary_pattern, feedback, re.IGNORECASE | re.DOTALL)
    
    analysis_content = analysis_match.group(1).strip() if analysis_match else None
    summary_content = summary_match.group(1).strip() if summary_match else None
    
    return analysis_content, summary_content

def extract_summary(feedback):
    """
    Extract the content between ###Summary### and ###End Summary###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        str or None: The extracted summary content. 
                     Returns None if the pattern is not found.
    """
    # Regex to match content between ###Summary### and ###End Summary###
    summary_pattern = r"###\s*Summary\s*###\s*(.*?)\s*###\s*End\s+Summary\s*###"
    
    summary_match = re.search(summary_pattern, feedback, re.IGNORECASE | re.DOTALL)
    
    summary_content = summary_match.group(1).strip() if summary_match else None
    
    return summary_content

def evaluate_score(experiment_data):
    try:
        score = float(experiment_data)

        if score <= 0.1209:
            score_prompt = "Scores below 0.1209 are guessed to be ineffective. All key points are likely to be ineffective.\n"
        else:
            score_prompt = "The score reaches above 0.1209, suggesting that some key points are likely to be effective.\n"

    except (ValueError, TypeError):
        score_prompt = "Unable to determine effectiveness due to non-numeric input.\n"

    return score_prompt


def experiment_result_summary_analysis(score_path, research_question, previously_analysis,summary_content,output_dir,index):
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    experiment_data = data[1]
    experiment_prompt = ""
    #The analysis is one step behind the experimental results.
    if len(experiment_data) > 1:
        for i in range(len(experiment_data)-1):
            score_prompt = evaluate_score(experiment_data[i][5])
            # score = float(experiment_data[i][5])
            # if score <= 0.1209:
            #     score_prompt = "Scores below 0.1209 are considered basically ineffective. The key points are basically ineffective"
            # else:
            #     score_prompt = "The score reaches above 0.1209,Some of the key points are effective"
            experiment_prompt += f"\nWe conducted the Experiment {i+1} as follows: The category selected for the experiment is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]}, Scientific Hypothesis Analysis:{previously_analysis[i]},The score of the experimental feedback:{experiment_data[i][5]}, Preliminary analysis results of the experimental feedback: "+ score_prompt 
            # f"Summary and Analysis of the single-run experiment:{summary_content[i]}"
    else:
        experiment_prompt = "Currently, there is no experimental information."
    last_experiment = experiment_data[-1]
    score_prompt = evaluate_score(last_experiment[5])
    # score = float(last_experiment[5])
    # if score <= 0.1209:
    #     score_prompt = "Scores below 0.1209 are guessed to be ineffective. All key points are likely to be ineffective.\n"
    # else:
    #     score_prompt = "The score reaches above 0.1209, Some of the key points are likely to be effective\n"
    num = len(experiment_data)
    new_experiment_prompt = f"\nnew experimental results:Experiment {num}: Category is {last_experiment[0]}, Hypothesis is {last_experiment[2]} Result is {last_experiment[5]}, Preliminary analysis results of the experimental feedback: "+ score_prompt
    key_points_file_path = os.path.join(output_dir, f'key_points_file_{index}.json')
    with open(key_points_file_path, 'r', encoding='utf-8') as json_file:
        key_points = json.load(json_file)
    gene_hypothesis_chem_key = [value for item in key_points for key, value in item.items() if str(last_experiment[1]) == str(key)]
    
    # generate_key_point = generate_key_point_prompt(research_question,last_experiment[2])
    # print(f"generate_key_point_prompt\n{generate_key_point}")
    # gene_hypothesis_chem_key = get_gene_hypothesis_with_retry(generate_key_point, api_request)
    prompt = f"""You are a chemistry expert tasked with addressing the chemical question: {research_question}. To address this issue, I conducted some experiments on the candidate scientific hypotheses for this scientific question. You need to analyze and summarize(record) the experimental results. Help to identify the chemical key points for solving the chemical problem. The following are the previously experimental results and analysis.\n{experiment_prompt}\n You need to refer to the previous content and focus on analyzing the new experimental results. The new experimental results that need to be analyzed are as follows:{new_experiment_prompt}\nThe key points of the scientific hypothesis are split, and the Role and Function of each key point are as follows:\n{gene_hypothesis_chem_key}
    A complete scientific hypothesis consists of multiple Chemical Key Points. The chemical category is classified based on the Chemical Key Points included in the scientific hypothesis. I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. An experimental feedback score below 0.1209 suggests that all the key points are likely ineffective. A score above 0.1209 indicates that some key points may effectively address the scientific problem.The higher the score, the more likely the hypothesis contains a greater number of effective Chemical Key Points. Experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple Chemical Key Points. The chemical category is classified based on the Chemical Key Points included in the scientific hypothesis. The experimental feedback score is the result of the combined effects of multiple Chemical Key Points. In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result. Therefore, when analyzing the scientific hypothesis, it is necessary to consider whether each Chemical Key Point is effective. When analyzing the effectiveness of key points in new experimental results, priority should be given to considering the scientific hypothesis feedback scores of similar or identical key points from previous experimental results and analysis, making a comprehensive judgment on their effectiveness.This process continuously refines the understanding of the mechanisms of chemical key points, helping to identify the correct key points. Summarize(record) should document the analysis results for each key point in the new experimental results, indicating whether it is likely effective, likely ineffective, or uncertain.
    Let’s think step by step. When you are analyzing and summarizing, first analyze the research question to clarify the experimental objectives. Identify the key factors that contribute to the ultimate goal of the experiment. Combine the preliminary analysis results of the experiment with previous Chemical Key Points and experimental results to analyze which key points and their functions are likely effective and which key points and functions may have been misunderstood, and include these findings in the analysis output. Focus on understanding the mechanisms through which these Chemical Key Points are likely to work effectively. If the experimental feedback score is higher than 0.1209, some key points are likely effective. You need to consider the scientific hypothesis feedback scores of similar or identical key points from previous experimental results and analysis to make a comprehensive judgment on their effectiveness. The analysis should include: ###Chemical Key Points### ###Mechanism of Action### This section explains the mechanism and action of the chemical issue. ###Effectiveness_Reasoning### This part integrates the mechanisms of Chemical Key Points and considers the scientific hypothesis feedback scores of similar or identical key points from previous experimental results and analysis to comprehensively determine whether the key point is effective. ###Effectiveness### Provide the effectiveness assessment as Guessed to be likely effective, Guessed to be likely ineffective, or Uncertain. Summarize based on the analysis. It is necessary to extract  ### Chemical Key Points ### and ### Effectiveness ### from the analysis. Note that effectiveness can only be Guessed to be likely effective, Guessed to be likely ineffective, or Uncertain.
    
    Let’s think step by step. For example, the chemical question: How can we improve the electrical performance of thermoelectric materials? The scientific hypothesis is to construct ion channels through freeze orientation, polymerize using polyvinyl alcohol (PVA), and add guanidine sulfate to synthesize a gel with good electrical performance. The experimental result is 0.8. Preliminary analysis results of the experimental feedback: The score reaches above 0.1209, suggesting that some key points are likely to be effective.
    ###Thought Process### First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials. What aspects are included in electrical performance (e.g., electrical conductivity, resistance)? To effectively solve the experimental goal, the focus should be on combinations of Chemical Key Points that can impact electrical conductivity and resistance. The following is the analysis and assessment of the key points.
    ###Analysis###
    ###Chemical Key Points###
    1.Freeze orientation: 
    ###Mechanism of Action###
    This technique is often used to create materials with a directional structure, which could enhance ionic conductivity. 
    ###Effectiveness_Reasoning### 
    Based on the scientific hypothesis feedback score of 0.8 for the key point, And combined with previous experimental feedback, high key point scores are likely effective. it is determined that using co-built ion channels can effectively enhance ion transport and improve the electrical performance of thermoelectric materials. Therefore, it is judged as effective.
    ###Effectiveness### Guessed to be likely effective
    ###Chemical Key Points###
    2.PVA polymerization
    ###Mechanism of Action###
    By using PVA with high molecular weight as the material matrix, it can provide certain mechanical properties. 
    ###Effectiveness_Reasoning### 
    The scientific hypothesis feedback score is 0.8, and it can provide certain mechanical properties. Enhancing ion transport by forming ion channels through PVA Therefore, this hypothesis is likely effective, but it cannot be fully confirmed and needs further analysis with subsequent scientific.
    ###Effectiveness### Uncertain
    ###Chemical Key Points###
    3.Guanidine sulfate
    ###Mechanism of Action###
    Guanidine sulfate, as a chemical reagent, may function by increasing the entropy difference to enhance performance, as it is currently unclear.
    ###Effectiveness_Reasoning### 
    Based on the scientific hypothesis feedback score of 0.8 and the mechanism analysis is not very clear. It needs to be confirmed with subsequent experimental results.
    ###Effectiveness### Uncertain
    ###End Analysis###
    ###Summary###
    1.Freeze orientation: Guessed to be likely effective
    2.PVA polymerization:Uncertain
    3.Guanidine sulfate:Uncertain
    ###End Summary###
    Note that the experimental score is obtained through the combined contribution of multiple Chemical Key Points. When analyzing effectiveness, it is essential to integrate thoughtful analysis and judgment. Analysis and Summary:It is necessary to identify the chemical key points in the scientific hypotheses and evaluate whether they align with the experimental feedback. Provide a corresponding summary.First, the analysis needs to strictly evaluate new experimental scientific hypothesis. Then, proceed with the summary.Summarize based on the analysis. It is necessary to extract ### Chemical Key Points ### and ### Effectiveness ### from the analysis. Note that effectiveness can only be Likely Effective, Likely Ineffective, or Uncertain.The output must include ###Analysis###、 ###End Analysis###and ###Summary### end with ###End Summary###The format is:
    ###Thought Process###
    Please output the thought process step by step.\n
    ###Analysis###
    ###Chemical Key Points###
    ###Mechanism of Action###
    ###Effectiveness_Reasoning### 
    ###Effectiveness### [Guessed to be likely effective, Guessed to be likely ineffective, or Uncertain]
    ###End Analysis###
    ###Summary###
    ###Chemical Key Points###
    ###Effectiveness###  [Guessed to be likely effective, Guessed to be likely ineffective, or Uncertain]
    ###End Summary###
         """
    return prompt
    
# def experiment_result_category_advice (score_path, research_question,existing_categories):
#     with open(score_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     experiment_data = data[1]
#     experiment_prompt = ""
#     for i in range(len(experiment_data)):
#         experiment_prompt += f"\nExperiment {i+1}: Category is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]}, Result is {experiment_data[i][5]}\n"
#     prompt = f"""
# You are a chemistry expert tasked with addressing the chemical question: {research_question}. I will provide you with candidate chemical categories  relevant to solving this problem, and you need to give suggestions on the next steps for choosing candidate chemical categories that could lead to better experimental feedback scores, based on existing experimental results, combining your thoughts and extensive chemical knowledge. Below are the candidate chemical categories.\n{existing_categories}\n
# Currently, we have obtained some experimental results. Since there are many scientific hypotheses within each category, we select scientific hypotheses from different categories for experimentation. I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. A score of 0.028 generally covers some of the key points. A single chemical category (or chemical point) cannot be tested in isolation; experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple chemical categories. Therefore, it is important to note that the experimental feedback score is the result of the combined effects of multiple chemical categories, not the result of a single chemical category. The following are the experimental results.\n {experiment_prompt}\n
# Let’s think step by step.When formulating your suggestions, first analyze the research question to clarify the experimental objectives. Identify the key factors that contribute to the ultimate goal of the experiment. Then, break down the experimental hypothesis into chemical key points and determine which chemical categories each element belongs to. Next, in light of the experimental goals, think about which combinations of chemical categories effectively address the objectives of the experiment. Focus on understanding the mechanisms through which these categories work effectively. Evaluate the contribution of each specific chemical category to the overall result. Please specify the percentage of contribution. Finally, reflect on your chemical knowledge, consider the existing experimental scores, and assess whether the mechanisms of action for each chemical category are correct in terms of achieving the experimental goals. Based on this analysis, provide clear recommendations from the candidate chemical categories for the next step, aiming to achieve better experimental feedback.Please note that the experimental feedback structure is arranged from high to low scores. After analyzing the scientific hypotheses with high feedback scores, it is equally important to examine the experimental feedback with low scores. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not achieve the expected results. These insights offer guidance on what to avoid in future hypotheses, effectively recommending steering clear of certain interfering or incorrect chemical points, thereby providing better guidance for selection.
# Please note that the experimental feedback structure is arranged from high to low scores. Each experimental hypothesis contains multiple scientific key points. For hypotheses with high experimental scores, the feedback recommends which key points should be included in future selections. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not work as expected. These insights offer guidance on what to avoid in future hypotheses and clearly specify which key points should be included next time.
# Let’s think step by step.For example, the chemical question: How can we improve the electrical performance of thermoelectric materials? First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials.What aspects are included in electrical performance (e.g., electrical conductivity, resistance)? The scientific hypothesis is to construct ion channels through freeze orientation, polymerize using polyvinyl alcohol (PVA), and add guanidine sulfate to synthesize a gel with good electrical performance. The experimental result is 0.8. Hypothesis breakdown and chemical key points:\nFreeze orientation: This technique is often used to create materials with a directional structure, which could enhance ionic conductivity. This hypothesis falls under the categories of Ion Channels and Material Structure Design. \nPVA polymerization, PVA polymerization falls under Polymer Design and Crosslink Density categories.\n Guanidine sulfate: Guanidine sulfate, as a chemical reagent, may function by increasing the entropy difference to enhance performance, as it is currently unclear which compounds belong to the Guanidine sulfate category.\nTo effectively solve the experimental goal, the focus should be on combinations of chemical categories that can impact electrical conductivity and resistance. By thinking through the effective mechanisms, the following chemical category combinations are worth focusing on:\nIon Channels: The structure and alignment of ion channels directly affect the material’s ionic conductivity, with key factors being the directionality of the ion channels. Freeze orientation technology could enhance conductivity by constructing aligned ion channels. \nContributions of the chemical categories to the overall result:\n Ion Channels: Creating ordered ion channels through freeze orientation can reduce resistance, enhance ionic conductivity, and thus improve electrical performance. Potential contribution: 50%\n Polymer Design: Optimizing the crosslink density and molecular structure of the polymer helps to enhance the mechanical strength and stability of thermoelectric materials, indirectly improving electrical performance. Potential contribution: 30% \n Guanidine sulfate may help improve ionic conductivity, adjusting the carrier concentration and further optimizing the electrical conductivity. Potential contribution: 20% \nEvaluation and Suggestions:The experimental result score of 0.8 indicates that some key points in the hypothesis are effective, with Ion Channels contributing significantly. Therefore, it is highly recommended to prioritize Ion Channels.
# Please note that the experimental feedback structure is arranged from high to low scores. After analyzing the scientific hypotheses with high feedback scores, it is equally important to examine the experimental feedback with low scores.For example, the hypothesis of improving gel conductivity and thermoelectric performance by adding heavy metals received an experimental feedback score of 0.0000065.  First, break down the key scientific points, which mention heavy metals and conductive gels. By analyzing the experimental results, the low scores indicate that the key points in the hypothesis are not recommended. Comparing the similarities and differences with higher-scoring scientific hypotheses can help explain the underlying mechanisms. For instance, the mechanism of ion channels may contribute to the electrical performance of gels, whereas the mechanism relying on metal conductivity to enhance material performance may have issues. Therefore, it is recommended to avoid approaches that depend on metal conductivity to improve performance.Each experimental hypothesis contains multiple scientific key points. For hypotheses with high experimental scores, the feedback recommends which key points should be included in future selections. For hypotheses with lower scores, a more detailed analysis is provided, highlighting which key points did not work as expected. These insights offer guidance on what to avoid in future hypotheses and clearly specify which key points should be included next time.Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than three.Based on the current experimental feedback and my chemical knowledge, here are the recommendations for the next step in the experiment:
# ###Advice###
# Suggested chemical categories to select:
# Ion Channels. Reason: The directional arrangement of ion channels is crucial for enhancing electrical conductivity. Freeze orientation technology is an effective method to create directional ion channels, which can directly influence the material's electrical performance. Strongly recommended to choose Ion Channels.
# Polymer Design Reason: Polyvinyl alcohol (PVA), as a polymer, plays a crucial role in adjusting the stability and conductivity of thermoelectric materials. Optimizing the crosslink density of PVA can effectively enhance the material's electrical performance. Consider selecting Polymer Design.
# It is recommended to avoid including certain chemical categories (the recommended chemical categories should not include them).
# By analyzing the low-scoring experiments, it is concluded that heavy metal components should not be included, as the scientific hypotheses containing heavy metals tend to have lower feedback scores. The analysis suggests this is due to environmental concerns and the limitations they impose on potential applications.The addition of heavy metals may disrupt the existing structure of the gel, leading to a decline in performance.Therefore, it is suggested that the mechanism relying on metal conductivity to enhance material performance may have issues, and it is recommended to avoid options containing these elements.
# ###End###The given advice should not be specific to the class. Instead, it should be summarized based on your understanding of the experimental feedback. Note that the key points to avoid should be based on the understanding of the experimental feedback, and specific suggestions regarding directions do not need to be detailed with numerical values.
# Please note that the suggestions provided should include the complete and correct names of the candidate chemical categories if they are recommended for selection. Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than three. Please analyze based on the key points of the scientific hypotheses derived from experimental feedback. Please note that before your final recommendation, add ###Advice###, and after the recommendation is completed, add ###End###.You need to provide expert recommendations to ensure that the chemical categories chosen for the experiments will yield better results.Please provide the thought process.Output format should strictly follow:
# ###The thought process is as follows:
# ###Advice### Suggestions based on experimental feedback ###End### Please think step by step and answer according to the requirements.
#         """
#     return prompt


def experiment_result_prompt (summary_content, summary_compilation,score_path):
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    experiment_data = data[1]
    experiment_prompt = ""
    if summary_compilation is not None:
        experiment_prompt += summary_compilation
    if len(experiment_data) > 0:
        for index in range(len(summary_content)):
            #Calculate the corresponding negative index in experiment_data, starting from -len(remaining_summary_data) and incrementing to -1.
            # print(f"\n\nlen(summary_content){len(summary_content)}")
            i = -(len(summary_content)) + index
            # print(f"i{i}")
            num = len(experiment_data)+i+1
            experiment_prompt += f"\nWe conducted the Experiment {num} as follows: The category selected for the experiment is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]},Result is {experiment_data[i][5]}\nSummary of the single-run experiment:{summary_content[i]}\n\n"
    else:
        experiment_prompt = "Currently, there is no experimental information."
    return  experiment_prompt




def experiment_result_category_advice (experiment_prompt,research_question,existing_categories,previously_analysis,score_path):
    prompt = f"""
You are a chemistry expert tasked with addressing the chemical question: {research_question}. I will provide you with candidate chemical categories relevant to solving this problem, and you need to give suggestions on the next steps for choosing candidate chemical categories that could lead to better experimental feedback scores, and output a list containing the categories you currently consider the best based on existing experimental results, combining your thoughts and extensive chemical knowledge. Below are the candidate chemical categories.\n{existing_categories}\n You need to analyze each candidate chemical category one by one and then, in combination with the results of previous experiments, provide suggestions that can effectively solve the scientific problem.
Currently, we have obtained some experimental results and have conducted analysis and summarized the findings. A single chemical category (or chemical point) cannot be tested in isolation; experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple chemical categories. The chemical category is classified based on the Chemical Key Points included in the scientific hypothesis. The experimental feedback score is the result of the combined effects of multiple Chemical Key Points. In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result.The following is the analysis of the experimental feedback on the scientific hypothesis\n {experiment_prompt}\n
I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. When the score reaches above 0.1209, there may be some Chemical Key Points that are effective in addressing the scientific problem. For the chemical categories in the scientific hypotheses that have been experimented on, if the experimental feedback score is high and the analysis result also deems it effective, then similar chemical categories can be recommended from the candidate chemical categories for analysis to see if they can effectively solve the scientific problem, and corresponding suggestions should be provided. On the other hand, if the experimental feedback score is low and the analysis result is also ineffective, then the reasons for the ineffectiveness of similar chemical categories in the candidate chemical categories should be analyzed and output as suggestions to prevent subsequent selections. When you analyze each chemical category in the candidate chemical categories, you need to combine the chemical problem, experimental feedback, and analysis results to comprehensively judge which experimental chemical key points they are more similar to, and thus determine whether they are useful.
When making suggestions. First analyze the research question to clarify the experimental objectives. Then, Analyze each candidate chemical category one by one. Combine the chemical problem, experimental feedback, and analysis results to determine whether each category can effectively solve the problem. Conduct reasoning and output the thought process and rationale. Finally, based on the analysis of each category, provide a comprehensive judgment and recommendation for the most effective category. And output a list containing the categories you currently consider the best.
Let’s think step by step. When formulating your suggestions, first analyze the research question to clarify the experimental objectives. Identify the key factors that contribute to the ultimate goal of the experiment. For example, the chemical question: How can we improve the electrical performance of thermoelectric materials? 
Then, analyze each candidate chemical category one by one. Combine the chemical problem and experimental feedback to determine whether each category can effectively solve the problem. Conduct reasoning and output the thought process and rationale.\n
Finally, based on the analysis of each category, provide a comprehensive judgment and recommendation for the most effective category. Based on the current categories and the analysis and summary of the experimental hypothesis, determine which key points are effective for the scientific question and which need to be avoided. Based on this analysis, provide clear recommendations from the candidate chemical categories for the next step, aiming to achieve better experimental feedback. For the effective key points involved in the analysis and summary, you should conduct further analysis and evaluation to determine whether they are truly effective. It is also worth considering mechanisms with similar principles to recommend for potential future selections.For the ineffective key points involved in the analysis and summary, you need to reflect on the reasons for their ineffectiveness and provide suggestions on how to avoid similar choices in the future.
Example output:
###The thought process is as follows:
First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials. What aspects are included in electrical performance (e.g. electrical conductivity, resistance)?
Then, We analyze each candidate chemical category while focusing on their mechanisms and expected contributions to the thermogalvanic devices' properties:
1. **Guanidine Salt**: Generally enhances the ionic conductivity of polymer electrolytes. This category can be reconsidered as it offers potential improvements regarding ionic pathways.
2. **Polymer Materials**: A core component regarding flexibility and structural support. Recommended due to known effectiveness in improving mechanical resilience and maintaining conductivity.
3. **Dual-Phase Freeze-Casting**: This can create structures that enhance thermal characteristics. It needs more feedback; uncertain if it specifically addresses the scientific problem.
4. **Hierarchical Pore Structures**: These could enhance diffusion paths and improve ionic conductivity.This technique is often used to create materials with a directional structure, which could enhance ionic conductivit.
###Advice###
Suggested chemical categories to select:
1.Ion Channels. Reason: The directional arrangement of ion channels is crucial for enhancing electrical conductivity. Hierarchical Pore Structures technology is an effective method to create directional ion channels, which can directly influence the material's electrical performance. Strongly recommended to choose Ion Channels.candidate chemical categories include oriented structures, stretch-induced orientation, and ionic channels, they may all be chemical categories that can effectively solve the problem
2.Polymer Materials Reason: Polyvinyl alcohol (PVA), as a polymer, plays a crucial role in adjusting the stability and conductivity of thermoelectric materials. Optimizing the crosslink density of PVA can effectively enhance the material's electrical performance. Consider selecting Polymer Design.
It is recommended to avoid including certain chemical categories (the recommended chemical categories should not include them).
By analyzing the low-scoring experiments, it is concluded that heavy metal components should not be included, as the scientific hypotheses containing heavy metals tend to have lower feedback scores. The analysis suggests this is due to environmental concerns and the limitations they impose on potential applications.The addition of heavy metals may disrupt the existing structure of the gel, leading to a decline in performance.Therefore, it is suggested that the mechanism relying on metal conductivity to enhance material performance may have issues, and it is recommended to avoid options containing these elements.
###End###
###Effective Categories###
["Ion Channels"]
###End###
Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than two. Please analyze based on the key points of the scientific hypotheses derived from experimental feedback. Please note that before your final recommendation, add ###Advice###, and after the recommendation is completed, add ###End###.You need to provide expert recommendations to ensure that the chemical categories chosen for the experiments will yield better results.Please provide the thought process.Output format should strictly follow:
###The thought process is as follows:
###Advice### Previous experimental category scores Suggestions based on experimental feedback ###End### ###Effective Categories###["Category Name you consider most effective"]###End###Please think step by step and answer according to the requirements.
        """
    return prompt

def experiment_result_summary_generalization (summary_content,research_question,score_path):
    # with open(score_path, 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    # experiment_data = data[1]
    # experiment_prompt = ""
    # for i in range(len(experiment_data)):
    #     experiment_prompt += f"\nExperiment {i+1}: Category is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]}, Result is {experiment_data[i][5]}\n"
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    experiment_data = data[1]
    experiment_prompt = ""
    if len(summary_content) > 0:
        #The analysis of the first scientific hypothesis has already been completed when carrying out this step.
        # for i in range(len(experiment_data)):
        #     experiment_prompt += f"\nExperiment {i+1}: Category is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]},Scientific Hypothesis Analysis:{previously_analysis[i]},Result is {experiment_data[i][5]} \n\n"
        for i in range(len(summary_content)):
            experiment_prompt += f"\nWe conducted the Experiment {i+1} as follows: The category selected for the experiment is {experiment_data[i][0]}, Hypothesis is {experiment_data[i][2]},Result is {experiment_data[i][5]}\nSummary of the single-run experiment:{summary_content[i]}\n\n"
    else:
        experiment_prompt = "Currently, there is no experimental information."
    prompt = f"""
You are a chemistry expert tasked with addressing the following chemical research question: {research_question}. To investigate this question, a series of experiments were conducted. For each experiment, a detailed analysis was performed, which involved the following steps:
Identifying and evaluating each key point of the hypothesis.
Speculating on the potential effectiveness of each key point.
Providing reflective feedback based on experimental outcomes.
The experimental results, including feedback and reflections, are documented as follows: {experiment_prompt}.
Your task is to analyze the experimental feedback and reflective records, simulate a human-like thought process, and provide a comprehensive summary. In your analysis, address the following:
Identify key points that consistently appeared ineffective across multiple experiments.
Identify key points that showed potential effectiveness based on experimental outcomes.
Provide a logical and evidence-based rationale for your conclusions, ensuring that all conclusions are derived from the experimental data and feedback.
When summarizing, consider the following:
The experiments are categorized under the theme: category. If the scientific hypotheses within this category consistently receive low feedback scores, explicitly state that hypotheses in this category may be ineffective.
Ensure that your summary integrates and synthesizes all historical experimental results and analyses, avoiding conclusions that are not supported by the provided data.
Output your analysis in the following format:
###Summary###
Your detailed summary here, reflecting the thought process, experimental evidence, and conclusions.
###End Summary###
Example output for reference:
###Summary###
In the first experiment, the hypothesis suggested that the chemical key point of ionic liquids might be effective in improving thermoelectric performance, while freeze alignment and guanidine sulfate were considered uncertain. Reflective analysis proposed that ionic liquids could enhance conductivity, thereby addressing the challenge of improving thermoelectric material performance. Consequently, further experiments focusing on ionic liquids were recommended. However, in Experiment 2, which tested ionic liquids, the feedback scores were low, indicating that ionic liquids did not perform as expected in the context of thermoelectric materials. Based on this, the reflection suggested exploring alternative key points, such as freeze alignment, with the hypothesis that freeze alignment could create ion channels to enhance conductivity. Experiment 3 was designed to test this hypothesis, and the feedback showed significant improvement compared to Experiment 2, confirming the potential effectiveness of freeze alignment as a key point. In summary, ionic liquids were found to be ineffective, while freeze alignment showed promise and warrants further investigation.
###End Summary###
        """
    return prompt




def experiment_result_category_final_advice (experiment_prompt, research_question,existing_categories_list,previously_analysis,score_path,category_list_advice):
    prompt = f"""
You are a chemistry expert tasked with addressing the chemical question: {research_question}. I hope you can help me provide suggestions on choosing effective classes to solve the problem. Below are the candidate classes. Please analyze each one to determine whether it can effectively address the chemical issue and provide a final recommendation.
Below are the candidate chemical categories.\n{category_list_advice}You need to give suggestions on the next steps for choosing candidate chemical categories that could lead to better experimental feedback scores, based on existing experimental results, combining your thoughts and extensive chemical knowledge.
We have obtained the following recommendations through analysis. Please integrate the experimental results and these recommendations to provide a final recommendation.The recommendations obtained are as follows:\n{existing_categories_list}\n
Before providing the final recommendation, analyze the similarities and differences between these recommendations, consider which ones can effectively solve this scientific problem, and present your thought process. Finally, provide a comprehensive final recommendation.
Currently, we have obtained some experimental results and have conducted analysis and summarized the findings. A single chemical category (or chemical point) cannot be tested in isolation; experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple chemical categories. The chemical category is classified based on the Chemical Key Points included in the scientific hypothesis. The experimental feedback score is the result of the combined effects of multiple Chemical Key Points. In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result.The following is the analysis of the experimental feedback on the scientific hypothesis\n {experiment_prompt}\n
I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. When the score reaches above 0.1209, there may be some Chemical Key Points that are effective in addressing the scientific problem. For the chemical categories in the scientific hypotheses that have been experimented on, if the experimental feedback score is high and the analysis result also deems it effective, then similar chemical categories can be recommended from the candidate chemical categories for analysis to see if they can effectively solve the scientific problem, and corresponding suggestions should be provided. On the other hand, if the experimental feedback score is low and the analysis result is also ineffective, then the reasons for the ineffectiveness of similar chemical categories in the candidate chemical categories should be analyzed and output as suggestions to prevent subsequent selections. 
When you integrate the suggestions to provide the final recommendation, you need to combine the chemical problem, experimental feedback, and recommendations obtained to comprehensively judge which experimental chemical key points are more effective.
Example output:
###The thought process is as follows:
First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials. What aspects are included in electrical performance (e.g. electrical conductivity, resistance)?
Then, We analyze each candidate chemical category while focusing on their mechanisms and expected contributions to the thermogalvanic devices' properties:
1. **Guanidine Salt**: Generally enhances the ionic conductivity of polymer electrolytes. This category can be reconsidered as it offers potential improvements regarding ionic pathways.
2. **Polymer Materials**: A core component regarding flexibility and structural support. Recommended due to known effectiveness in improving mechanical resilience and maintaining conductivity.
3. **Dual-Phase Freeze-Casting**: This can create structures that enhance thermal characteristics. It needs more feedback; uncertain if it specifically addresses the scientific problem.
4. **Hierarchical Pore Structures**: These could enhance diffusion paths and improve ionic conductivity.This technique is often used to create materials with a directional structure, which could enhance ionic conductivit.
###Advice###
Suggested chemical categories to select:
1.Ion Channels. Reason: The directional arrangement of ion channels is crucial for enhancing electrical conductivity. Hierarchical Pore Structures technology is an effective method to create directional ion channels, which can directly influence the material's electrical performance. Strongly recommended to choose Ion Channels.candidate chemical categories include oriented structures, stretch-induced orientation, and ionic channels, they may all be chemical categories that can effectively solve the problem
2.Polymer Materials Reason: Polyvinyl alcohol (PVA), as a polymer, plays a crucial role in adjusting the stability and conductivity of thermoelectric materials. Optimizing the crosslink density of PVA can effectively enhance the material's electrical performance. Consider selecting Polymer Design.
It is recommended to avoid including certain chemical categories (the recommended chemical categories should not include them).
By analyzing the low-scoring experiments, it is concluded that heavy metal components should not be included, as the scientific hypotheses containing heavy metals tend to have lower feedback scores. The analysis suggests this is due to environmental concerns and the limitations they impose on potential applications.The addition of heavy metals may disrupt the existing structure of the gel, leading to a decline in performance.Therefore, it is suggested that the mechanism relying on metal conductivity to enhance material performance may have issues, and it is recommended to avoid options containing these elements.
###End###
Please note that in the suggestions, the recommended key points should not exceed two, while the key points to avoid should be no fewer than two. Please analyze based on the key points of the scientific hypotheses derived from experimental feedback. Please note that before your final recommendation, add ###Advice###, and after the recommendation is completed, add ###End###.You need to provide expert recommendations to ensure that the chemical categories chosen for the experiments will yield better results.Please provide the thought process.Output format should strictly follow:
###The thought process is as follows:
###Advice### Previous experimental category scores   Suggestions based on experimental feedback ###End### Please think step by step and answer according to the requirements.
        """
    return prompt
      
# def experiment_summary_category_prompt(category_advice, research_question, existing_categories):
#     prompt = f"""
#     You are a chemistry expert tasked with addressing the chemical question: {research_question} I will provide you with candidate chemical categories relevant to solving this problem, and you need to analyze and identify which categories are the most effective for addressing this challenge. The output format must strictly adhere to the provided category names .The Effective Categories must be in list format, and the list cannot contain more than 3 elements. Of course, if you are very certain that one specific candidate chemical category can solve the problem, you can recommend just that category.
#     Let’s think step by step.First, you need to analyze the research question and clarify what the experimental goal is. Then, based on the suggestions from the experimental feedback, think about which chemical category combinations are effective in solving the experimental goal. Using your chemical knowledge, analyze and select the three most effective categories from the candidate chemical categories.
#     Here is some suggestions from the experimental feedback to help you choose Effective Categories.\n{category_advice}\n Please note that the suggested categories for selection are only recommendations. Do not directly output the recommended categories. You need to identify relevant categories from the candidate chemical categories, carefully selecting the ones you believe are effective. Once you've selected them, output the category names correctly and completely from the candidate chemical categories.The categories must be in list format, and the list cannot contain more than 3 elements. Below are the candidate chemical categories.\n
#     {existing_categories} Please note that Effective Categories selection should be strictly from the candidate chemical categories. Please verify the output format.The output format is as follows
#     ###Effective Categories###
#     ["Category Name Chosen from chemical categories"]
#     ###End###\nPlease think step by step and answer according to the requirements.
#         """
#     return prompt
def experiment_summary_category_prompt(category_advice, research_question, existing_categories):
    prompt = f"""
    You are a chemistry expert tasked with addressing the chemical question: {research_question} I will provide you with candidate chemical categories relevant to solving this problem, and you need to analyze and identify which categories are the most effective for addressing this challenge. The output format must strictly adhere to the provided category names .The Effective Categories must be in list format, and the list can only contain one element.
    Let’s think step by step.First, you need to analyze the research question and clarify what the experimental goal is. Then, based on the suggestions from the experimental feedback, think about which chemical category combinations are effective in solving the experimental goal. Using your chemical knowledge, analyze and select the three most effective categories from the candidate chemical categories.
    Here is some suggestions from the experimental feedback to help you choose Effective Categories.\n{category_advice}\n  I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. When the score reaches above 0.1209, there may be some Chemical Key Points that are effective in addressing the scientific problem. Please note that the suggested categories for selection are only recommendations. Do not directly output the recommended categories. You need to identify relevant categories from the candidate chemical categories, carefully selecting the ones you believe are effective. Once you've selected them, output the category names correctly and completely from the candidate chemical categories.The categories must be in list format, and the list can only contain one element. Below are the candidate chemical categories.\n
    {existing_categories} Please note that Effective Categories selection should be strictly from the candidate chemical categories. Please provide the thought process.Please verify the output format.The output format is as follows
    ###The thought process is as follows###
    During the thought process, it is necessary to combine the specific scientific question to provide answers and choose the category. Please provide a detailed explanation for the selection, along with analysis and feasibility predictions.
    ###Effective Categories###
    ["Category Name Chosen from chemical categories"]
    ###End###\nPlease think step by step and answer according to the requirements.
        """
    return prompt

def experiment_result_hypothesis_advice(experiment_prompt, research_question: str,  effective_categories: List[str], cur_category: str,hypotheses,previously_analysis,score_path) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""

You are a chemistry expert tasked with addressing the chemical question: {research_question}. I will provide you with candidate chemical hypotheses relevant to solving this problem, and you need to give suggestions on which chemical hypothesis to choose next. Analyze each candidate chemical hypotheses one by one. Combine the chemical problem, experimental feedback, and analysis results to determine which chemical hypothesis can effectively solve the problem.
Currently, we have obtained some experimental results and have conducted analysis and summarized the findings. A single chemical category (or chemical point) cannot be tested in isolation; experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple chemical categories. The chemical category is classified based on the Chemical Key Points included in the scientific hypothesis. The experimental feedback score is the result of the combined effects of multiple Chemical Key Points. In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result.The following is the analysis of the experimental feedback on the scientific hypothesis\n {experiment_prompt}\n
I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. When the score reaches above 0.1209, there may be some Chemical Key Points that are effective in addressing the scientific problem. For the chemical categories in the scientific hypotheses that have been experimented on, if the experimental feedback score is high and the analysis result also deems it effective, then similar chemical hypotheses containing similar chemical categories can be recommended from the candidate chemical hypotheses for analysis to see if they can effectively solve the scientific problem, and corresponding suggestions should be provided. On the other hand, if the experimental feedback score is low and the analysis result is also ineffective, then the reasons for the ineffectiveness of similar chemical hypotheses containing similar chemical categories in the candidate chemical hypotheses should be analyzed and output as suggestions to prevent subsequent selections. When you analyze each chemical hypothesis in the candidate chemical hypotheses, you need to combine the chemical problem, experimental feedback, and analysis results to comprehensively judge which chemical hypothesis can effectively solve the problem. Based on the analysis, the effective chemical categories {effective_categories} have been determined, and currently, we are analyzing the {cur_category} category. The candidate chemical hypotheses of this category are as follows: {hypotheses}
When making suggestions. First analyze the research question to clarify the experimental objectives. Then, Analyze each candidate chemical hypotheses one by one. Combine the chemical problem, experimental feedback, and analysis results to determine whether each hypothesis can effectively solve the problem. Conduct reasoning and output the thought process and rationale. Finally, based on the analysis of each hypothesis, provide a comprehensive judgment and recommendation for the most effective hypothesis.Using your chemical knowledge, analyze and provide suggestions on selecting the most suitable scientific hypotheses.Some scientific hypotheses may include descriptions of the expected performance of the hypothesis. In fact, do not trust any descriptions regarding the expected performance or effect of the hypothesis. Instead, focus solely on the core chemical points and predict which hypothesis would be more effective for the research question if tested in real experiments. 
Let’s think step by step. When formulating your suggestions, first analyze the research question to clarify the experimental objectives. Identify the key factors that contribute to the ultimate goal of the experiment. For example, the chemical question: How can we improve the electrical performance of thermoelectric materials? Then, Analyze each candidate chemical hypotheses one by one. Combine the chemical problem, experimental feedback, and analysis results to determine whether each hypothesis can effectively solve the problem. Conduct reasoning and output the thought process and rationale. Finally, based on the analysis of each hypothesis, provide a comprehensive judgment and recommendation for the most effective hypothesis.Based on this analysis, provide clear recommendations from the candidate chemical hypotheses for the next step, aiming to achieve better experimental feedback. For the effective key points involved in the analysis and summary, you should conduct further analysis and evaluation to determine whether they are truly effective. It is also worth considering mechanisms with similar principles to recommend for potential future selections.For the ineffective key points involved in the analysis and summary, you need to reflect on the reasons for their ineffectiveness and provide suggestions on how to avoid similar choices in the future.
Example output:
###The thought process is as follows:
First, analyze the question: The experimental goal is to improve the electrical performance of thermoelectric materials. What aspects are included in electrical performance (e.g. electrical conductivity, resistance)?
Then, We analyze each candidate chemical category while focusing on their mechanisms and expected contributions to the thermogalvanic devices' properties:
1.Hypothesis 1 (Guanidine Sulfate in PVA Hydrogel): This hypothesis emphasizes a flexible thermogalvanic device with directional channels, leveraging known effective materials and mechanisms. The key point of directional channels is basically consistent with the effective key point of ionic channels in previous experimental feedback. The use of guanidine sulfate is consistent with enhancing mechanical strength and thermoelectric performance. More recommended.
2.Hypothesis 3 (Hierarchical l-tyrosine Hydrogel Composites): This proposal centers on a composite matrix that focuses on exploiting both mechanical resilience and thermoelectric improvements through targeted structural design. The hierarchical l-tyrosine was previously judged as an ineffective key point and is not recommended. The hydrogel was not involved in previous experiments, but considering its role in thermoelectric performance is only supportive, it is not recommended.
###Advice###
Recommended Scientific Hypothesis Key Points:
1.Ionic Channels: Includes ionic channels that enhance ionic transport to improve thermoelectric efficiency.
2.PVA Aggregation: Contains PVA aggregation to provide mechanical support for thermoelectric materials. This key point is supported by previous feedback.
Key Points to Avoid:
1.Hierarchical l-Tyrosine: Previously judged as an ineffective key point and not recommended. Analysis suggests that using this material may interact with thermoelectric redox pairs, affecting efficiency.
2.Cross-Linking Mechanisms: Avoid hypotheses that rely on poorly defined cross-linking strategies, as previous experiments highlighted their role as a limitation.
Based on this advice, I recommend focusing on the following scientific hypotheses:
**Hypothesis 1 (Guanidine Sulfate in PVA Hydrogel):** This hypothesis emphasizes a flexible thermogalvanic device with directional channels, leveraging known effective materials and mechanisms. Utilization of guanidine sulfate aligns with enhancing mechanical strength and thermoelectric performance.
### End ###
Based on the current categories and the analysis and summary of the experimental hypothesis, determine which key points are effective for the scientific question and which need to be avoided. Then, analyze each scientific hypothesis one by one. Combine the chemical problem and experimental feedback to determine whether each hypothesis can effectively solve the problem. Conduct reasoning and output the thought process and rationale. Finally, based on the analysis of each scientific hypothesis, provide a comprehensive judgment and recommendation a scientific hypothesis that contains the most effective key points and is most likely to be effective.

Please note that in the suggestions, the recommended Scientific Hypothesis Key Points should not exceed two, while the key points to avoid should be no fewer than two. Please note that in the suggestions The given advice should  should be summarized based on your understanding of the experimental feedback.Finally, provide a comprehensive recommendation for no more than one scientific hypothesis.
You need to provide clear and specific suggestions, aiming to ensure that the choice of scientific hypotheses will lead to better experimental results.
Output format should strictly follow:
###The thought process is as follows:
###Advice### Suggestions based on experimental feedback. ###End### Please think step by step and answer according to the requirements.### End ###
"""
    return prompt


def experiment_summary_hypothesis_prompt(hypothesis_advice, research_question: str,  effective_categories: List[str], cur_category: str, hypotheses: List[Tuple[str, str]]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    You are a chemistry expert tasked with analyzing the chemical question: {research_question} You currently identify effective chemical categories {effective_categories} and analyze the {cur_category} category. You need to combine suggestions and your own reasoning to choose which the best scientific hypothesis can effectively solve the problem.
    The scientific hypotheses contained within this category are {hypotheses}. Here is some suggestions from the experimental feedback to to help you select the best hypothesis within this chemical category: \n{hypothesis_advice}\n
    The thought process should be as follows:
    Let’s think step by step. First, you need to analyze the research question and clarify what the experimental goal is. Then, based on the suggestions from the experimental feedback, think about which chemical scientific hypotheses, characterized by specific features, could be effective in solving the experimental goal. Using your chemical knowledge, analyze and provide suggestions on selecting the most suitable scientific hypotheses.Some scientific hypotheses may include descriptions of the expected performance of the hypothesis. In fact, do not trust any descriptions regarding the expected performance or effect of the hypothesis. Instead, focus solely on the core chemical points and predict which hypothesis would be more effective for the research question if tested in real experiments. 
    You need to combine suggestions and your own reasoning to choose what you believe is the best scientific hypothesis. Please provide the thought process. Please select what you believe is the best scientific hypothesis under the current category; only one scientific hypothesis can be output.
    Please ensure the output strictly follows the format below.\n
    Output Format
    ###The thought process is as follows:
    ###Scientific Hypothesis###
    {{"Category Name Chosen from Existing Categories":["id of Scientific Hypothesis","Scientific Hypothesis"]}}
    ###End###Please think step by step and answer according to the requirements.
    """
    return prompt

def save_method_hypotheses(hypotheses,index,index2,output_dir):
    """
    Save the list of hypotheses to a JSON file.

    Args:
        hypotheses (list): The list of hypotheses to save.
    
    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_output_{index}_{index2}.json")
    try:
        with open(file_path, 'w',encoding='utf-8') as file:
            json.dump(hypotheses, file, indent=4)
        print(f"Hypotheses saved to {file_path}")
    
    except Exception as e:
        print(f"Error saving hypotheses: {e}")
   
   


def filter_current_dict(base_dir, index, hypotheses_file):
    """
    Filters out the hypotheses from `current_dict` that match the first element of the lists
    in the `hypotheses_file`.

    Args:
        current_dict (dict): The dictionary where values are lists of numbers or strings.
        hypotheses_file (str): Path to the JSON file containing hypotheses to compare.

    Returns:
        dict: The filtered `current_dict` with matching values removed.
    """
    file_name = f"output_class_{index}.json"
    file_path = os.path.join(base_dir, file_name)

    with open(file_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
        # You can process the `data` as required here
        # print(f"Successfully read {file_name}")
        current_dict = data.get("current_dict", {})
        # existing_categories = data.get("existing_categories", None)
        print(f"Successfully read {file_name}")
        # return current_dict, existing_categories
        # return data  # Return the data for further processing if needed  
    
    try:
        # Read the hypotheses file
        with open(hypotheses_file, 'r',encoding='utf-8') as file:
            hypotheses_data = json.load(file)
            print(f"Hypotheses loaded from {hypotheses_file}")
        #{key:[key,hypothesis]}
        # Extract the result_hypothesis from the first element of each hypothesis list
        result_hypotheses = []
        for hypothesis in hypotheses_data:
            for key, value in hypothesis.items():
                if isinstance(value, list) and value:
                    result_hypothesis = str(value[0])  # Take the first element and convert to string
                    result_hypotheses.append(result_hypothesis)
        
        print(f"Extracted hypotheses to remove: {result_hypotheses}")
        
        # Filter the current_dict by comparing the list items
        filtered_dict = {}
        keys_with_empty_values = [] 
        for key, value in current_dict.items():
            # Convert all items in the list to strings
            value_as_str = [str(item) for item in value]
            
            # Keep the key-value pair only if it's not in the result_hypotheses
            filtered_values = [item for item in value_as_str if item not in result_hypotheses]
            if filtered_values:
                filtered_dict[key] = filtered_values
            else:
            #  keys_with_empty_values 
                keys_with_empty_values.append(key)
        print(f'\nkeys_with_empty_values\n\n{keys_with_empty_values}')
        
        print("Filtering complete.")
        # filtered_existing_categories = [
        # category for category in existing_categories if category not in keys_with_empty_values]
        # filtered_existing_categories = [category for category in existing_categories if not any(key in category for key in keys_with_empty_values)]
        filtered_existing_categories = list(filtered_dict.keys())
        save_data = {
        "current_dict": filtered_dict,
        "existing_categories": filtered_existing_categories
    }
        
        with open(file_path, 'w',encoding='utf-8') as f:
            json.dump(save_data, f, indent=4)
        print(f"Successfully saved processed data to {file_path}")
        return filtered_dict,filtered_existing_categories

    except Exception as e:
        print(f"Error processing files: {e}")
        return None   

def sort_experiment_data(file_path):
    """
    Read the JSON file at the specified path, sort the elements in data[1] based on the last item (score) in each element,
    and save the sorted experiment data to a new file.

    :param file_path: Path to the input JSON file
    :param output_file_path: Path to save the output sorted JSON file
    :return: None
    """
    
    # Read the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract data[1], which is the experiment data list
    experiment_data = data[1]

    # Sort the experiment data based on the last item (score) in each element
    experiment_data_sorted = sorted(experiment_data, key=lambda x: x[-1], reverse=True)

    # Combine the original data[0] with the sorted experiment data
    new_data = [data[0], experiment_data_sorted]

    # Write the sorted data to the output JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(new_data, file, ensure_ascii=False, indent=4)

    print(f"Data has been sorted and saved to {file_path}")
    return file_path

def deduplicate_by_first_value(result):
    seen = set()
    unique_result = []
    
    for item in result:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list) and value:
                    first_value = value[0]
                    if first_value not in seen:
                        seen.add(first_value)
                        unique_result.append(item)
                    break  
    return unique_result

def handle_summary_analysis(index, output_dir,score_path,research_question,analysis_content=None, summary_content=None):
    # Check if the input parameters are valid
 
    if index is None or output_dir is None:
        raise ValueError("The index and output_dir must not be empty")

    # Generate the file name and file path.
    analysis_file_name = f"analysis_content_{index}.json"
    analysis_file_name = os.path.join(output_dir, analysis_file_name)

    summary_file_name = f"summary_content_{index}.json"
    summary_file_name = os.path.join(output_dir, summary_file_name)

    summary_compilation_file_name = f"summary_compilation_content_{index}.json"
    summary_compilation_file_name = os.path.join(output_dir, summary_compilation_file_name)

    # If the file does not exist, create the file and write an empty list into it
    if not os.path.exists(analysis_file_name):
        with open(analysis_file_name, 'w',encoding='utf-8') as f:
            json.dump([], f)  
    if not os.path.exists(summary_file_name):
        with open(summary_file_name, 'w',encoding='utf-8') as f:
            json.dump([], f)  
    if not os.path.exists(summary_compilation_file_name):
        with open(summary_compilation_file_name, 'w',encoding='utf-8') as f:
            json.dump([], f)  

    # Read the contents of the existing file.
    with open(analysis_file_name, 'r',encoding='utf-8') as f:
        analysis_data  = json.load(f)
    with open(summary_file_name, 'r',encoding='utf-8') as f:
        summary_data = json.load(f)
    with open(summary_compilation_file_name,'r',encoding='utf-8') as f:
        summary_compilation_data = json.load(f)
 
    remaining_summary_data = []
    if analysis_content is not None:
        analysis_data.append(analysis_content)
        with open(analysis_file_name, 'w',encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=4)
    if summary_content is not None:
        with open(score_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        experiment_data = data[1]
        num = len(experiment_data)
        summary = F"The following guessed results were obtained in the {num} experiment:\n "+ summary_content
        summary_data.append(summary)
        with open(summary_file_name, 'w',encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=4)

        # print(f"summary_data{summary_data}")
        total_length = len(summary_data)
        remainder = total_length % 5
        # Initialize the result variable.
        compilation_data = []
        # remaining_summary_data = []
        #Summary Compilation is conducted every five times, while keeping the remaining_summary_data up-to-date with the latest experimental feedback from 0 to 9. summary_compilation_data: [1, 2, 3, 4, 5] remaining_summary_data: [6, 7, 8, 9, 10]  #remaining_summary_data: [6, 7, 8, 9, 10, 11, 12, 13, 14]
        if remainder != 0:
            remaining_summary_data = summary_data[-5-remainder:]
        else:
            # If there is no remainder (i.e. it is a multiple of 5), the last five elements are designated as remaining_summary_data
            remaining_summary_data = summary_data[-5:]
            # The rest are designated as summary_compilation_data
            compilation_data = summary_data[:-5]
            prompt = experiment_result_summary_generalization (compilation_data,research_question,score_path)
            summary_compilation = validate_summary_compilation(prompt, api_request)
            num = len(compilation_data)
            summary = F"The following is a summary of the analysis and speculation on the results of the first {num} rounds of experiments:\n "+ summary_compilation

            summary_compilation_data.append(summary)

            # If there is summary_compilation_data, save it to a new file.
            if compilation_data:
                with open(summary_compilation_file_name, 'w', encoding='utf-8') as f:
                    json.dump(summary_compilation_data, f, ensure_ascii=False, indent=4)
    # print(f"\n\nanalysis_data{analysis_data}\n\nremaining_summary_data{remaining_summary_data}\n\n")
    return analysis_data,remaining_summary_data, summary_compilation_data[-1] if summary_compilation_data else None

    # return analysis_data,summary_data if summary_data else None
 





def validate_summary_analysis(feedback, prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
    # while retry_count < max_retries:
    #     if not isinstance(categories, list) or len(categories) > 3:
            
            analysis_content, summary_content= extract_summary_analysis(feedback)
            if analysis_content is not None and summary_content is not None:
                return analysis_content, analysis_content
                return analysis_content, summary_content
            prompt += """Please make sure to check and follow the output format strictly as per the following format,The output must include ###Analysis###、 ###End Analysis###and ###Summary### end with ###End Summary###The format is:###Thought Process######Analysis### ###Chemical Key Points###
            ###Mechanism of Action###
            ###Analysis###
            ###Effectiveness### [Effective, Ineffective, Uncertain]
            ###End Analysis###
            ###Summary###
            ###Chemical Category##
            ###Mechanism of Action###
            ###Effectiveness### [Effective, Ineffective, Uncertain]
            ###End Summary###"""
            retry_count += 1
            print(f"Attempt {retry_count} failed. Retrying...")
            feedback = api_request(prompt)
            print(f"Retry feedback:\n\n{feedback}")
            # continue
      
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return None,None


def validate_summary_compilation(prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
    # while retry_count < max_retries:
    #     if not isinstance(categories, list) or len(categories) > 3:
            print(f"\nsummary_compilation_prompt\n\n{prompt}")
            feedback = api_request(prompt)
            print(f"\nsummary_compilation_feedback\n\n{feedback}")
            summary_content= extract_summary(feedback)
            if summary_content is not None:
                return summary_content
            prompt += """Please make sure to check and follow the output format strictly as per the following format,The output must include###Summary### end with ###End Summary###"""
            retry_count += 1
            print(f"Attempt {retry_count} failed. Retrying...")
            feedback = api_request(prompt)
            print(f"Retry feedback:\n\n{feedback}")
            # continue
      
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return None




def validate_advice_category(feedback, prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
    # while retry_count < max_retries:
    #     if not isinstance(categories, list) or len(categories) > 3:
            ex_advice,ex_category = extract_advice_list(feedback)
            print(f"\n\nExtract_Advice\n\n{ex_advice}\n Extract_list\n\n{ex_category}")
            if ex_advice is not None and ex_category is not None:
                return ex_advice,ex_category
            if ex_advice is  None:
                prompt += """Please make sure to check and follow the output format strictly as per the following format,The output format is as follows:###Advice### Suggestions based on experimental feedback ###End### ###Effective Categories###["Category Name you consider most effective"]###End###
                """
            else:
                prompt +="""The selected output Category is list.###Effective Categories###["Category Name you consider most effective"]###End###"""
            retry_count += 1
            print(f"Attempt {retry_count} failed. Retrying...")
            feedback = api_request(prompt)
            print(f"Retry feedback:\n\n{feedback}")
            # continue
      
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return None

def validate_advice(feedback, prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
    # while retry_count < max_retries:
    #     if not isinstance(categories, list) or len(categories) > 3:
            ex_advice = extract_advice(feedback)
            print(f"\n\nExtract_Advice\n\n{ex_advice}")
            if ex_advice is not None:
                return ex_advice
            prompt += """Please make sure to check and follow the output format strictly as per the following format,The output format is as follows:###Advice### Suggestions based on experimental feedback ###End### 
            """
            retry_count += 1
            print(f"Attempt {retry_count} failed. Retrying...")
            feedback = api_request(prompt)
            print(f"Retry feedback:\n\n{feedback}")
            # continue
      
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return None

def extract_thought_process(feedback):
    match = re.search(r"###\s*The thought process is as follows\s*###\s*(.*?)\s*###\s*Effective Categories\s*###", feedback, re.DOTALL)
    return match.group(1).strip() if match else None


def validate_and_retry_categories_thought_process(feedback, prompt, api_request,existing_categories):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        
        categories,feedback = validate_and_retry_categories(feedback, prompt, api_request,existing_categories)
        thought_process = extract_thought_process(feedback)
        if isinstance(categories, list) and thought_process is not None:
        # if isinstance(existing_categories, list):
            print(f"thought_process \n\n{thought_process}")
            return categories,thought_process

        elif thought_process is None:
            print("Error: Failed to extract thought_process. Retrying...")
            prompt += """Please strictly follow the output format below. It must include ###The thought process is as follows### ###Effective Categories### and ###End###."""

        retry_count += 1
        print(f"Attempt {retry_count} failed. Retrying...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")
        # continue
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return categories,thought_process


def update_json_with_experiment_choice(index, output_dir, effective_categories, thought_process):
    # Read the JSON file
    
    summary_file_name = f"summary_content_{index}.json"
    summary_file_name = os.path.join(output_dir, summary_file_name)
    try:
        with open(summary_file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return

    # Combine the string
    if effective_categories:
        categories_str = ", ".join(map(str, effective_categories))
    else:
        categories_str = "No categories selected"
    print(categories_str)
    new_entry = f"Based on the current experimental results, the analysis process of the guessed results is as follows: {thought_process}. After analysis, the final selected experiment category is {categories_str}"

    # Ensure the JSON file is a list
    if isinstance(data, list):
        # Retrieve the last element and ensure it is a string
        last_entry = str(data[-1])
    
        # Append the new entry to the last element
        updated_entry = last_entry + " " + new_entry  # Adding a space for better readability
        # Replace the last element with the updated one
        data[-1] = updated_entry
        
        # data.append(new_entry)  # Append to the list
    else:
        print("Error: JSON structure is not a list.")
        return

    # Save the updated JSON file
    try:
        with open(summary_file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Updated JSON file successfully saved to {summary_file_name}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def choose_hypothesis_method(filepath, research_question_filepath, data_path, index, score_path, hypotheses_file,output_dir):
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)  
    #   The outfile is the hypotheses_file from the previous round.   hypotheses_output_{index}.json
    current_dict, existing_categories = filter_current_dict(data_path, index, hypotheses_file)
    # process_json_files(data_path,index)
    # current_dict, existing_categories = process_json_files(data_path,index)
    research_question = read_research_question(research_question_filepath, index)
    # Sort the scientific hypotheses.
    # score_path = sort_experiment_data(score_path)
    previously_analysis,summary_content,summary_compilation = handle_summary_analysis(index, output_dir,score_path,research_question )
    # print(f"previously_analysis\n{previously_analysis}")
    summary_analysis_prompt = experiment_result_summary_analysis(score_path, research_question, previously_analysis,summary_content,output_dir,index)
    print(f"\nexperiment_result_summary_analysis_prompt\n{summary_analysis_prompt}\n")
    feedback = api_request(summary_analysis_prompt)
    print(f"\nexperiment_result_summary_analysis_feedback\n\n{feedback}")
    # summary_analysis = extract_summary_analysis(feedback)
    analysis_content, summary_content = validate_summary_analysis(feedback, summary_analysis_prompt , api_request)
    print(f"\n\nextract analysis \n\n {analysis_content }\n\n extract summary\n\n{summary_content}")
    previously_analysis,summary_content,summary_compilation = handle_summary_analysis(index, output_dir,score_path,research_question, analysis_content, summary_content)
    experiment_prompt = experiment_result_prompt (summary_content, summary_compilation,score_path)
    # print(f"previously_analysis\n{previously_analysis}")
    # category_advice_prompt = experiment_result_category_advice (score_path, research_question,existing_categories)
    batch_size = 10
    category_advice_list = []
    category_list_advice = []
    total_elements = len(existing_categories)
    for i in range(0, total_elements, batch_size):
        # Get the elements of the current batch
        batch = existing_categories[i:i + batch_size]
        category_advice_prompt = experiment_result_category_advice (experiment_prompt,research_question,batch,previously_analysis,score_path)
        print(f"\ncategory_advice_prompt\n{category_advice_prompt}\n")
        feedback = api_request(category_advice_prompt)
        print(f"\ncategory_advice_prompt_feedback\n\n{feedback}")
        category_advice,ex_category = validate_advice_category(feedback, category_advice_prompt, api_request)
        text_str = str(category_advice)
        text = f"Recommendation {i}:"+text_str
        category_advice_list.append(text)
        category_list_advice.extend(ex_category)
    print(f"----------------Second-level analysis-------------------------\n\ncategory_list_advice:\n{category_list_advice}")
    batch_size = 8
    category_advice_list_2 = []
    category_list_advice_2 = []
    total_elements = len(category_list_advice)
    for i in range(0, total_elements, batch_size):
        # Get the elements of the current batch
        batch = category_list_advice[i:i + batch_size]
        category_advice_prompt = experiment_result_category_advice (experiment_prompt , research_question,batch,previously_analysis,score_path)
        print(f"\ncategory_advice_prompt\n{category_advice_prompt}\n")
        feedback = api_request(category_advice_prompt)
        print(f"\ncategory_advice_prompt_feedback\n\n{feedback}")
        category_advice,ex_category = validate_advice_category(feedback, category_advice_prompt, api_request)
        text_str = str(category_advice)
        text = f"Recommendation {i}:The rationale for recommending {ex_category}"+text_str
        category_advice_list_2.append(text)
        category_list_advice_2.extend(ex_category)
    category_advice_prompt = experiment_result_category_final_advice (experiment_prompt , research_question,category_advice_list_2,previously_analysis,score_path,category_list_advice_2)
    # category_advice_prompt = experiment_result_category_final_advice (summary_content, research_question,category_advice_list,previously_analysis,score_path,category_list_advice)
    # category_advice_prompt = experiment_result_category_advice (summary_content, research_question,category_list_advice,previously_analysis,score_path)
    print(f"\ncategory_advice_final_prompt\n{category_advice_prompt}\n")
    feedback = api_request(category_advice_prompt)
    print(f"\ncategory_advice_final_prompt_feedback\n\n{feedback}")
    category_advice = validate_advice(feedback, category_advice_prompt, api_request)
    # category_advice = validate_advice(feedback, category_advice_prompt, api_request)
    # category_advice = extract_advice(feedback)
    # print(f"category_advice\n\n{category_advice}")
    # category_prompt = experiment_summary_category_prompt(score_path, research_question, existing_categories )
    category_prompt = experiment_summary_category_prompt(category_advice, research_question, existing_categories )
    print(f"\ncategory_prompt\n{category_prompt}")
    feedback = api_request(category_prompt)
    print(f"\ncategory_feedback\n\n{feedback}")
    
    effective_categories, thought_process  = validate_and_retry_categories_thought_process(feedback, category_prompt, api_request,existing_categories)
    # effective_categories = validate_and_retry_categories(feedback,category_prompt, api_request,existing_categories)
    ###Store the thought process of selecting the category in the summary.
    update_json_with_experiment_choice(index, output_dir, effective_categories, thought_process)
    
    result = []
    for cur_category in effective_categories:
        hypotheses = generate_hypotheses (data,index, cur_category, current_dict)
        # hypothesis_advice_prompt = experiment_result_hypothesis_advice(score_path, research_question,  effective_categories, cur_category,hypotheses)
        hypothesis_advice_prompt = experiment_result_hypothesis_advice(experiment_prompt, research_question,  effective_categories, cur_category,hypotheses,previously_analysis,score_path)
        print(f"\nhypothesis_advice_prompt\n{hypothesis_advice_prompt}\n")
        feedback = api_request(hypothesis_advice_prompt)
        print(f"\nhypothesis_advice_prompt_feedback\n\n{feedback}")

        hypothesis_advice = validate_advice(feedback, hypothesis_advice_prompt, api_request)
        # hypothesis_advice = extract_advice(feedback)
        print(f"\n\nhypothesis_advice\n\n{hypothesis_advice}")
        hypothesis_prompt = experiment_summary_hypothesis_prompt(hypothesis_advice, research_question,  effective_categories, cur_category, hypotheses)
        print(f"\n\nhypothesis_prompt\n\n{hypothesis_prompt}")
        feedback = api_request(hypothesis_prompt)
        print(f"hypothesis_feedback\n\n{feedback}")
        scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request)
        if scientific_hypothesis:
            result.append(scientific_hypothesis)
        else:
            print(f"Skipping category {cur_category} due to invalid scientific hypothesis format.")
            
        # save_hypotheses(result,index,output_dir)
    # save_method_hypotheses(result,index,index2,output_dir)
    result = deduplicate_by_first_value(result)
    with open(hypotheses_file, 'w',encoding='utf-8') as file:
            json.dump(result, file, indent=4)
    print(f"Hypotheses saved to {hypotheses_file}")
    return result , hypotheses_file
#outfie  patrh hypotheses_output_{index}.json
    file_path = save_hypotheses(result,index,output_dir)
    return file_path
    
    save_hypotheses(result,index,output_dir)
    return result
    



        
if __name__ == "__main__":
    data_path = "./simulation_experiment/main"  # 
    filepath = "./gdth_and_gene_hyp_add_id.json"
    research_question_filepath = "./research_question.json"
    num_iterations = 3  # 设置循环的次数
    output_dir =  "./out/out_cache"
    # 调用 main 函数
    choose_hypothesis_main(filepath, research_question_filepath,data_path,num_iterations,output_dir)

#    Note that the numbering must be consecutive, and the numbering of new categories should follow the previous sequence.