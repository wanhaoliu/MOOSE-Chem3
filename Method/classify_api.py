import json
import ast
from typing import List, Dict, Tuple
# import requests
import re
import os,sys
from gpt_api import api_request

sys.stdout.reconfigure(encoding='utf-8')

def extract_categories(feedback):
    """
    Extract the content between ###Categories### and ###End Categories###, including the brackets [ ],
    and convert the extracted string into an actual list.
    
    Args:
        feedback (str): The input text to search within.
    
    Returns:
        list: Extracted list or None if the pattern is not found.
    """
    # Regex to extract content between ###Categories### and ###End Categories###, including brackets [ ]
    # match = re.search(r"###\s*Categories\s*###\s*(\[[^\[\]]*\])\s*###\s*END\s*Categories\s*###", feedback, re.DOTALL)
    match = re.search(r"###\s*Categories\s*###\s*(\[.*?\])\s*###\s*End\s*Categories\s*###", feedback, re.DOTALL)
    if match:
        # Extract the matched content (the list as a string)
        list_str = match.group(1).strip()

        # Convert the string into an actual list using ast.literal_eval
        try:
            list_content = ast.literal_eval(list_str)
            return list_content
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing the list: {e}")
            return None
    else:
        return None





def extract_category_assignment(feedback):
    """
    Extract the dictionary between ###Category Assignment### and ###END Category Assignment###.

    Args:
        feedback (str): The input text to search within.

    Returns:
        dict: Extracted dictionary or None if the pattern is not found.
    """
    # Regex to match content between ###Category Assignment### and ###END Category Assignment###
    match = re.search( r"###\s*Category\s*Assignment\s*###.*?(\{.*?\}).*?###\s*END\s*Category\s*Assignment\s*###",  feedback, re.DOTALL)
    if match:
        content = match.group(1).strip()
        try:
            # Convert the content to a dictionary using `ast.literal_eval`
            return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            # If parsing fails, return None
            return None
    return None


def read_hypotheses(data: str, start: int, batch_size: int, sub_index: int) -> Tuple[List[Tuple[str, str]], int, int]:
    """
    Reads a batch of hypotheses from the JSON file, iterating through all elements in data[1].
    """
    hypotheses = []
    while sub_index < len(data[1]):
        current_data = data[1][sub_index]
        i = start
        keys = list(current_data.keys()) # keys is id
        while len(hypotheses) < batch_size and i < len(keys):
            key = keys[i]
            hypotheses.append((key, current_data[key]))
            i += 1
        # If batch is filled, return the current state
        if len(hypotheses) >= batch_size:
            return hypotheses, i, sub_index
        # Move to the next part of data[1] if current one is exhausted
        start = 0
        sub_index += 1
        return hypotheses, 0, sub_index  
    

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

def generate_prompt(research_question: str, hypotheses: List[Tuple[str, str]]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    We are working on the scientific problem: {research_question}.
    You are an experienced chemistry expert. Below, I will provide you with scientific hypothesis. Please identify the chemical key points that constitute the hypothesis, chemical key points are the core key elements for effectively solving the scientific problem. The analysis of chemical key points needs to be combined with specific scientific problem for consideration, identifying which key points in the scientific hypothesis can solve these problems. When identifying chemical key points, note that each substance may be a chemical key point. Please carefully analyze and judge. At the same time, if multiple substances exist and are related, such as potassium ferricyanide and potassium ferrocyanide, they are a pair of oxidizing and reducing substances. Therefore, such a pair of substances belongs to one chemical key point. The basis for classification is that they have the same function or need to exist together to work. These chemicals should be considered as one key point. Additionally, identify the results—effects or phenomena caused by these chemical key points. These represent the achievements or effects of the experiment. Note that the results are the effects or phenomena caused by these chemical key points, so when performing the output, pay attention to outputting the chemical key points, not the results. At the same time, you need to pay attention that the scientific hypothesis to be analyzed will contain validation methods for the experiment, such as using elemental analysis to verify the properties of a certain substance, etc. These are validations of the scientific hypothesis, not scientific key points. Scientific key points are the core key elements for effectively solving the scientific problem, not the validation methods. When identifying the key points in the hypothesis, it's important to combine them with the scientific problem. Please note that if the key points included in the scientific question are also present in the scientific hypothesis, they should not be output as key points. For example, if the scientific problem is about how to improve the mechanical properties of MXene nanosheets, then the MXene nanosheets mentioned in the hypothesis as being enhanced by the addition of liquid metal should be considered as a prerequisite, not a chemical key point. In this case, the liquid metal would be the chemical key point. Before output, please check whether the chemical key point includes the substance in the scientific problem. If it does, please remove it.the chemical key points should is a list, with the format strictly following:["chemical key points"]
    Example:
    ###Chemical Key Points###
    1.PVA (Polyvinyl Alcohol)
    Role and Function: Polyvinyl alcohol (PVA) hydrogel acts as the base material, providing structural support and mechanical performance for thermoelectric gels.
    2.Gdm₂SO₄ (Guanidine Sulfate)
    Role and Function: Guanidine sulfate (Gdm₂SO₄) is integrated into the PVA hydrogel to improve thermoelectric performance. The introduction of guanidine salt increases solvent entropy and effectively enhances thermopower.
    3.Directional Freezing Method
    Role and Function: By employing directional freezing technology, aligned channels are created, enhancing the electrical conductivity and mechanical strength of the material.
    4.Potassium Ferricyanide and Potassium Ferrocyanide (K₃[Fe(CN)₆] / K₄[Fe(CN)₆])
    Role and Function: These compounds are crucial electrolytes that facilitate redox reactions within the polymer gel. The presence of these ions enhances ion mobility and conductivity due to their ability to undergo reversible redox processes, thereby boosting the thermoelectric properties of the gel
    ###Results###
    Carnot-relative Efficiency
    The Carnot-relative efficiency of the FTGA exceeds 8%.
    Thermopower and Mechanical Robustness
    Thermopower and mechanical robustness are enhanced, outperforming traditional quasi-solid-state thermoelectric cells.
    ###Categories###["PVA (Polyvinyl Alcohol)","Gdm₂SO₄ (Guanidine Sulfate)","Directional Freezing Method"]###End Categories###
    The format is as follows:
    ###Categories###["chemical key points"]###End Categories### Please think step by step and answer according to the requirements.
    Please analyze below.hypotheses is {hypotheses}"""

    return prompt

def extract_chemical_key_points(feedback):
    match = re.search(r"(###Chemical Key Points###.*?)(?=###Results###)", feedback, re.DOTALL)
    return match.group(1).strip() if match else None


def classification_categories_prompt(research_question, existing_categories: List[str]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
  We are working on the research question: {research_question}. Now we have some candidate chemical categories for the research question. Please use your chemical knowledge and analyze whether there are any similarities between these categories. If so, please summarize them again. Below are the existing categories:\n{existing_categories}\nClassification needs to be tailored to specific scientific problems. For example, if the problem is How to improve the ionic conductivity of a gel, based on the analysis of the problem, which categories can improve the ionic conductivity of the gel? If the current existing_categories include stretch-induced alignment, electric field-assisted alignment, freeze-casting alignment, then based on chemical knowledge, all of them aim to improve the gel's electrical conductivity by constructing ion channels. Therefore, these can be grouped into the category of "ionic channels".
  Please analyze and categorize the existing_categories based on this principle, and output the result in the following format:###Categories###["Category Name:Brief explanation/overview of the category"]###END Let’s think step by step.
    """
    return prompt

def generate_check_prompt(research_question: str, hypotheses: List[Tuple[str, str]], existing_categories: List[str]) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    We are working on the research question: {research_question} Now we have many chemical categories related to solving this problem. These chemical categories are derived from the chemical hypotheses through key point analysis and summarization. We want to analyze which categories of the chemical categories are included in the scientific hypothesis. If the key points in these categories are the ones that the scientific hypothesis possesses, we will place the ID of the scientific hypothesis in the corresponding chemical categories.
    A scientific hypothesis can contain different Chemically Key Points, and each Chemically Key Point is a category. Therefore, each chemical scientific hypothesis belongs to multiple chemical categories based on different chemical points. During the classification process, priority is given to categorizing by the same chemical names (substance names, experimental method names, synthesis technique names, etc.): For example, if the scientific hypothesis is "Using the freeze-casting method to fabricate PVA gels to create ionic channels," the hypothesis contains PVA, freeze-casting method, and ionic channels. The ID of this hypothesis should be placed in the corresponding or similar categories. Then, classification is done based on similar mechanisms: For example, a hypothesis utilizing cryo-alignment techniques to fabricate ion channels would simultaneously belong to the ion channel engineering category, cryopolymerization methodology group, and hierarchical architecture classification, given that cryogenic processing inherently induces stratified structural characteristics. To ensure the accuracy and completeness of the classification, please evaluate and categorize based on the consistency of substance names and the similarity of mechanisms of action to prevent any omissions in categorization.
    The chemical categories are as follows\n{existing_categories}\nPlease note that the format for chemical categories is Category Name
    Based on this principle: You need to break down the scientific hypothesis candidates into chemical key points, analyze which category each key point belongs to, and then place the corresponding scientific hypothesis IDs into the appropriate categories name. A scientific hypothesis may belong to multiple categories name.The category assignment of scientific hypotheses is in dictionary format. with the format strictly following: {{"Category Name":[IDs belonging to this category]}}The output should be in dictionary format, where the keys are category names, and the values are lists of scientific hypothesis IDs that belong to each category.If the current hypothesis ID does not belong to the candidate category, there is no need to output it. Only output the chemical category that the current hypothesis ID belongs to, following the format.The output should be in dictionary format, where the keys are category names, excluding the corresponding category description.
    The format is as follows:
    ###Category Assignment###
    {{"Category Name":[IDs belonging to this category]}}
    ###END Category Assignment### Let’s think step by step.
    Below are the scientific hypothesis candidates that need to be categorized.
    """
    for key, hypothesis in hypotheses:
        prompt += f"{key}: {hypothesis}\nPlease note that the hypothesis ID is {key}."
    return prompt

# def save_to_storage(index, current_dict, existing_categories,output_dir):
#     """
#     Save the current state of current_dict and existing_categories.
    
#     Args:
#         index (int): The current index to be saved.
#         current_dict (dict): The dictionary containing category assignments.
#         existing_categories (list): The list of existing categories.
#     """
#     os.makedirs(output_dir, exist_ok=True)
#     # file_path = os.path.join(output_dir, f"output_class_{index}_init.json")
#     # file_path_2 = os.path.join(output_dir, f"output_class_{index}_orig_init.json")
#     file_path = os.path.join(output_dir, f"output_class_{index}.json")
#     file_path_2 = os.path.join(output_dir, f"output_class_{index}_orig.json")
#     save_data = {
#         "current_dict": current_dict,
#         "existing_categories": existing_categories
#     }
#     with open(file_path, 'w',encoding='utf-8') as f:
#         # import json
#         json.dump(save_data, f, indent=4)
#     with open(file_path_2, 'w',encoding='utf-8') as file:
#             json.dump(save_data, file, indent=4)
#     print(f"Hypotheses saved to {file_path} and {file_path_2}")
#     print(f"Saved data for index {index} to {file_path}")


def save_to_storage(index, current_dict, existing_categories, output_dir):
    """
    Save the current state of current_dict and existing_categories.
    
    Args:
        index (int): The current index to be saved.
        current_dict (dict): The dictionary containing category assignments.
        existing_categories (list): The list of existing categories.
        output_dir (str): The directory where the output files will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract keys from current_dict and update existing_categories
    existing_categories = list(current_dict.keys())
    
    file_path = os.path.join(output_dir, f"output_class_{index}.json")
    file_path_2 = os.path.join(output_dir, f"output_class_{index}_orig.json")
    
    save_data = {
        "current_dict": current_dict,
        "existing_categories": existing_categories
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=4)
    
    with open(file_path_2, 'w', encoding='utf-8') as file:
        json.dump(save_data, file, indent=4)
    
    print(f"Hypotheses saved to {file_path} and {file_path_2}")
    print(f"Saved data for index {index} to {file_path}")

def validate_existing_categories(feedback, prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 10
    retry_count = 0
    while retry_count < max_retries:
        existing_categories = extract_categories(feedback)
        chemical_key_points = extract_chemical_key_points(feedback)

        if isinstance(existing_categories, list) and chemical_key_points is not None:
        # if isinstance(existing_categories, list):
            print(f"chemical key points is list. \n\n{existing_categories}")
            return existing_categories,chemical_key_points
        elif not isinstance(existing_categories, list):
            print(f"Error: Extracted  chemical key points is not a valid list. Received:\n\n{existing_categories}")
            prompt += """Please verify and output in the correct list format. ###Categories###["chemical key points","chemical key points"]###End Categories### The  chemical key points must be a list. At the same time, ensure the output format is as follows: ###Categories###[chemical key points,chemical key points]###End Categories###"""
        elif chemical_key_points is None:
            print("Error: Failed to extract valid Gene Hypothesis Key. Retrying...")
            prompt += """Please strictly follow the output format below. It must include ###Chemical Key Points###, ###Results###, ###Categories###, and ###End Categories### Please follow the output example to include ###Chemical Key Points###, ###Results###, ###Categories###, and ###End Categories###."""

        retry_count += 1
        print(f"Attempt {retry_count} failed. Retrying...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")
        # continue
    print("Critical Error: Could not extract a valid summary_analysis after retries.")         
    return None,None
# def validate_existing_categories(existing_categories, pro_existing_categories, prompt, api_request, max_retries=5):
#     """
#     Validate whether existing_categories is a list and contains pro_existing_categories' content.
#     If not, update the prompt and retry up to max_retries times.

#     Args:
#         existing_categories (list or other): The existing categories to validate.
#         pro_existing_categories (list): The list of mandatory categories that should be included.
#         prompt (str): The initial prompt used for the API request.
#         api_request (callable): Function to make an API request.

#     Returns:
#         list: Validated existing categories or None if validation fails after retry.
#     """
#     for retries in range(max_retries):

#         # Ensure existing_categories is a list
#         if not isinstance(existing_categories, list):
#             print(f"Error: Extracted existing categories is not a valid list. Received:\n\n{existing_categories}")
#             prompt += """Please verify and output in the correct list format. ###Categories###["chemical key points"]###End Categories### 
            
#             The existing categories must be a list. At the same time, ensure the output format is as follows: ###Categories###[Category Name]###End Categories###If no new categories are added, the output format should be:###Categories###[]###End Categories###"""
#             retry_feedback = api_request(prompt)
#             print(f"Retry feedback (Attempt {retries + 1}):\n\n{retry_feedback}")
#             existing_categories = extract_categories(retry_feedback)
#             if not isinstance(existing_categories, list):
#                 # retries += 1
#                 continue  # Retry if still not a valid list
#         new_categories = [cat for cat in existing_categories if cat not in pro_existing_categories]
#         print(f"\nnew_categories\n{new_categories}")
#         pro_existing_categories.extend(new_categories)
#         # existing_categories = pro_existing_categories
#         return pro_existing_categories
        # If existing_categories is None or not a list, skip further validation
        # if existing_categories is None:
        #     print(f"Error: existing_categories is None. Skipping further validation.")
        #     continue  # Retry if `existing_categories` is None

        # Check if mandatory categories are included
        # new_categories = [cat for cat in pro_existing_categories if cat not in existing_categories]
        # if missing_categories:
        #     print(f"Error: Missing mandatory categories: {missing_categories}")
        #     prompt += f" Note that the content of the existing categories list should include all the elements of {pro_existing_categories}. If new categories are added, please append them to the end.The existing categories must be a list. Please verify and output in the correct list format"
        #     retry_feedback = api_request(prompt)
        #     print(f"Retry feedback after checking missing categories (Attempt {retries + 1}):\n\n{retry_feedback}")
        #     existing_categories = extract_categories(retry_feedback)
        #     if not isinstance(existing_categories, list):
        #         continue
        #     # Revalidate the missing categories after retry
        #     missing_categories = [cat for cat in pro_existing_categories if cat not in existing_categories]
        #     if not missing_categories:
        #         return existing_categories  # Successfully validated after retry
        #     continue  # Retry if still missing categories
        # return existing_categories

    print(f"Error: Validation failed after {max_retries} retries. Returning None.")
    return None

def validate_classification_categories(existing_categories, prompt, api_request, max_retries=5):
    """
    Validate whether existing_categories is a list and contains pro_existing_categories' content.
    If not, update the prompt and retry up to max_retries times.

    Args:
        existing_categories (list or other): The existing categories to validate.
        pro_existing_categories (list): The list of mandatory categories that should be included.
        prompt (str): The initial prompt used for the API request.
        api_request (callable): Function to make an API request.

    Returns:
        list: Validated existing categories or None if validation fails after retry.
    """
    for retries in range(max_retries):
        # Ensure existing_categories is a list
        if not isinstance(existing_categories, list):
            print(f"Error: Extracted existing categories is not a valid list. Received:\n\n{existing_categories}")
            prompt += """ Please verify and output in the correct list format. At the same time, ensure the output format is as follows: ###Categories###[Category Name:Brief explanation/overview of the category]###End Categories###"""
            retry_feedback = api_request(prompt)
            print(f"Retry feedback (Attempt {retries + 1}):\n\n{retry_feedback}")
            existing_categories = extract_categories(retry_feedback)
            if not isinstance(existing_categories, list):
                # retries += 1
                continue  # Retry if still not a valid list
            return existing_categories
    print(f"Error: Validation failed after {max_retries} retries. Returning None.")
    return None
def validate_category_assignment(category_assignment, prompt, api_request, max_retries=5):
    """
    Validate whether category_assignment is a dictionary and contains the correct format.
    If not, update the prompt and retry up to max_retries times.

    Args:
        category_assignment (dict or other): The category assignment to validate.
        prompt (str): The initial prompt used for the API request.
        api_request (callable): Function to make an API request.

    Returns:
        dict: Validated category assignment or None if validation fails after retry.
    """
    for retries in range(max_retries):
        # Ensure category_assignment is a dictionary
        if not isinstance(category_assignment, dict):
            print(f"Error: Extracted category assignment is not a valid dictionary. Received:\n\n{category_assignment}")
            print("Retrying API request to ensure a valid dictionary is returned...")
            prompt = prompt + """The category assignment must be in dictionary format. Please verify the output format. At the same time, ensure the output format is as follows:    ###Category Assignment###{"Category Name":[IDs belonging to this category]}###END Category Assignment###"""
            retry_feedback = api_request(prompt)
            print(f"Retry feedback (Attempt {retries + 1}):\n\n{retry_feedback}")
            category_assignment = extract_category_assignment(retry_feedback)
            # Recheck if the result is a dictionary
            if not isinstance(category_assignment, dict):
                print(f"\nCritical Error: Retried API request still did not return a valid dictionary. Received: {category_assignment}")
                print("Skipping current iteration due to invalid data format.")
                continue  # Skip to next iteration

        # If the category_assignment is valid, return it
        return category_assignment

    print(f"Error: Validation failed after {max_retries} retries. Returning None.")
    return None

def process_classify(filepath,research_question_filepath,index,output_dir):
    # Configuration
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)         
    existing_categories = [] 
    pro_existing_categories =  []
    batch_size = 1
    start = 0
    # start = 180
    # sub_index = 0
    sub_index = index
    num_index = sub_index
        # Define the file path for saving existing categories
    output_file_path = os.path.join(output_dir, f'existing_categories_{index}.json')
    
    # Check if the file exists
    if os.path.exists(output_file_path):
        # Read from the existing file
        with open(output_file_path, 'r', encoding='utf-8') as file:
            existing_categories = json.load(file)
        print(f"Existing categories loaded from {output_file_path}")
        return existing_categories  # Return the categories from the file

    os.makedirs(output_dir, exist_ok=True)
    key_points_file_path = os.path.join(output_dir, f'key_points_file_{index}.json')
    os.makedirs(output_dir, exist_ok=True)
    chemical_key_points_list = []
    
    key_points_class_id_path = os.path.join(output_dir, f'key_points_class_id_{index}.json')
    key_points_class_id = []
    while True:
        # Read hypotheses
        research_question = read_research_question(research_question_filepath, sub_index)
        # hypotheses, start, sub_index = read_reverse_hypotheses (data, start, batch_size, sub_index)
        hypotheses, start, sub_index = read_hypotheses(data, start, batch_size, sub_index)       
        if not hypotheses:
            print(f"no hypotheses break ")
            if num_index < sub_index:
            # num_index += 1  # Increment sub_index
                print(f"*****************{pro_existing_categories}****************************")
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    json.dump(pro_existing_categories, file, ensure_ascii=False, indent=4)
                print(f"Existing categories saved to {output_file_path}")
                with open(key_points_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(chemical_key_points_list, json_file, ensure_ascii=False, indent=4)
                print(f"File saved to {key_points_file_path}")
                with open(key_points_class_id_path, 'w', encoding='utf-8') as id_file:
                    json.dump(key_points_class_id, id_file, ensure_ascii=False, indent=4)
                print(f"ID File saved to {key_points_class_id}")               
            return pro_existing_categories
        print(f"------------------Processing hypotheses batch starting at {sub_index}, end {start}---------------------------------")
        prompt = generate_prompt(research_question, hypotheses)
        # print(prompt)
        feedback = api_request(prompt)
        print(f"\n\nprocess_classify_feedback\n\n{feedback}")
        # existing_categories = extract_categories(feedback)
        # print(f"\n\nexisting_categories\n\n{existing_categories}\n\n")
        # existing_categories = validate_existing_categories(feedback, prompt, api_request)
        existing_categories,chemical_key_points = validate_existing_categories(feedback, prompt, api_request)
        result_dict = {}
        # hypotheses[0] is tuple
        key = hypotheses[0][0]
        # print(f"key {key}\n\n")
        value = chemical_key_points
        result_dict[key] = value
        # print(result_dict)
        chemical_key_points_list.append(result_dict)
        # print(chemical_key_points_list)
        # existing_categories = validate_existing_categories(existing_categories, pro_existing_categories, prompt, api_request,max_retries=5)
        # pro_existing_categories.append(existing_categories)
        if existing_categories is not None:
            pro_existing_categories.extend(existing_categories)
            for category in existing_categories:
                class_dict = {category: [hypotheses[0][0]]}
                key_points_class_id.append(class_dict)
                # print(f"key_points_class_id{class_dict}")

            
        else:
            print("existing_categories is None, skipping extension.")  
        # pro_existing_categories.extend(existing_categories)
        
        if num_index < sub_index:
            # num_index += 1  # Increment sub_index
            print(f"*****************{pro_existing_categories}****************************")

            with open(output_file_path, 'w', encoding='utf-8') as file:
                json.dump(pro_existing_categories, file, ensure_ascii=False, indent=4)
            print(f"Existing categories saved to {output_file_path}")
            with open(key_points_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(chemical_key_points_list, json_file, ensure_ascii=False, indent=4)
            print(f"File saved to {key_points_file_path}")
           
            with open(key_points_class_id_path, 'w', encoding='utf-8') as id_file:
                json.dump(key_points_class_id, id_file, ensure_ascii=False, indent=4)
            print(f"ID File saved to {key_points_class_id}") 
            return pro_existing_categories
    
def process_check_classify(filepath,research_question_filepath,existing_categories,index,output_dir = "."):
    # Configuration
    output_file_path = os.path.join(output_dir, f"output_class_{index}.json")
    
    # Check if the output file already exists
    if os.path.exists(output_file_path):
        print(f"File {output_file_path} already exists. Skipping processing.")
        return  # Skip further processing if the file exists

    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)         
    batch_size = 1
    start = 0
    sub_index = index
    num_index = index
    current_dict = {}  # Initialize an empty dictionary
    while True:
        # Read hypotheses
        # existing_categories_temp = existing_categories
        research_question = read_research_question(research_question_filepath, sub_index)
        hypotheses, start, sub_index = read_hypotheses(data, start, batch_size, sub_index)       
        if not hypotheses:
              if num_index < sub_index:
                print(f"The classification result of the {num_index}-th scientific hypothesis:\n\n{current_dict}")
                current_dict = update_current_dict(output_dir, current_dict, index)
                save_to_storage(num_index, current_dict, existing_categories,output_dir)
                break
            
        prompt = generate_check_prompt(research_question, hypotheses,existing_categories)
        print(prompt)
        feedback = api_request(prompt)
        print(f"feedback\n\n{feedback}")
        category_assignment = extract_category_assignment(feedback)
        print( f"category_assignment\n\n{category_assignment}")
        category_assignment = validate_category_assignment(category_assignment, prompt, api_request, max_retries=5)

        for key, values in category_assignment.items():
            key = key.strip().lower()
            if key in current_dict:
                #Use set to remove duplicates and avoid adding the same values repeatedly.
                current_dict[key] = list(set(current_dict[key] + values)) 
                # current_dict[key].extend(values)  # Append values to the existing key
            else:
                current_dict[key] = values  # Add new key-value pair

        if num_index < sub_index:
                print(f"The classification result of the {num_index}-th scientific hypothesis:\n\n{current_dict}")
                
                current_dict = update_current_dict(output_dir, current_dict, index)
                save_to_storage(num_index, current_dict, existing_categories,output_dir)
                break
        #         current_dict = {}  # Reset dictionary for the new sub_index
        #         num_index += 1  # Increment sub_index
        # if sub_index>=index+1:
        #     break
        
        
        
def update_current_dict(output_dir, current_dict, index):
    # Construct the path for saving the file.
    key_points_class_id_path = os.path.join(output_dir, f'key_points_class_id_{index}.json')

    # Attempt to read the existing data.
    if os.path.exists(key_points_class_id_path):
        with open(key_points_class_id_path, 'r', encoding='utf-8') as id_file:
            data = json.load(id_file)


    # Convert all dictionary keys in the data to lowercase.
    for item in data:
        # 确保字典的键转化为小写
        for key in list(item.keys()):
            item[key.lower()] = item.pop(key)
            


    for key, value in current_dict.items():
        key_lower = key.lower()  

    # Check if there is an identical category.
    
        for item in data:
            if key_lower in item:
                data_values = item[key_lower]
                # Check if the values in `current_dict` exist within the values in `data`.

                for val in data_values:
                    # 
                    if str(val) not in map(str,value):
                        value.append(str(val))  # If the value does not exist, add it.
                    # 
                    elif str(val) not in map(str, value):
                        print(f"Warning: val: {val} not in value: {value}")
                    else:
                        # why we can overlook this situation
                        pass
    return current_dict  



def chemical_classification_prompt (research_question, batch):
    prompt =f"""For specific chemical problems, we extract different chemical points from multiple scientific hypotheses. You need to analyze and categorize each point based on the scientific problem, and determine whether they belong to one of three categories: effective, ineffective, or uncertain. The classification criteria are based on whether these points can directly address the specific chemical problem. If they can effectively solve the problem, they are classified as effective chemical points. If the mechanism involved in the point cannot be confirmed, since the classification of points is based on elements, some elements that interact together may be separated. For example, if the problem is to improve electrical performance but the element's role is to improve material stability, stability is a prerequisite for improving electrical performance. In this case, the point may interact with other points to have an effect, and it should be classified as uncertain. If the point similar to verifying and testing chemical results cannot solve the chemical problem, it is classified as ineffective, such as methods like mechanical testing or infrared analysis that cannot improve electrical performance and Merely characterizing the performance does not solve the chemical problem.
    For example, the scientific problem is: How to improve the electrical performance of thermoelectric materials? The chemical points to be analyzed are: Cryogenic orientation technology, PVA (Polyvinyl Alcohol), Elemental analysis, and Cyclic bending test. Let's analyze step by step, starting with the explanation of each chemical point and then analyzing whether it can effectively solve the scientific problem.
    1.Cryogenic Orientation
    Explanation: Cryogenic orientation is a method of forming an oriented structure by freezing, which can create ion channels.
    Effectiveness Analysis: The scientific problem is improving the electrical performance of thermoelectric materials, which requires ion transport. Cryogenic orientation can form ion channels, which can effectively improve ion transport rate. Therefore, it is effective for solving the scientific problem and can be classified as effective.
    Conclusion: Effective. Cryogenic orientation technology can effectively enhance the ionic conductivity of thermoelectric materials, so it is an effective chemical point.
    2.PVA (Polyvinyl Alcohol)
    Explanation: PVA is a water-soluble polymer with good mechanical properties and thermal stability. It is often used as a matrix material to provide support and stability in thermoelectric materials.
    Effectiveness Analysis: PVA can act as a matrix material for thermoelectric materials. While it provides good structural support, its direct contribution to improving electrical performance is limited. Stable mechanical properties are also a prerequisite for enhancing electrical performance, but it is uncertain whether it will interact with other points to effectively improve electrical performance.
    Conclusion: Uncertain. PVA, as a matrix material, does not significantly improve electrical performance, mainly providing mechanical support. However, stable mechanical properties are a prerequisite for improving electrical performance. Therefore, it is uncertain whether it will interact with other points to effectively enhance electrical performance.
    3.Elemental Analysis
    Explanation: Elemental analysis is a method for determining the content and chemical composition of various elements in a material. Through this method, one can understand the distribution of electrons and ions in the material and predict its electrical properties.
    Effectiveness Analysis: Elemental analysis itself is a diagnostic tool and does not directly improve the electrical performance of materials. However, it can provide data support for material optimization, such as analyzing whether the concentration of certain elements helps to enhance electrical conductivity.
    Conclusion: Uncertain. Elemental analysis does not directly affect electrical performance, but it provides necessary data support to help optimize materials. Therefore, it is not a directly effective chemical point, but it has the potential to be a helpful tool.
    4.Cyclic Bending Test
    Explanation: The cyclic bending test is used to assess a material’s durability and stability under repeated bending. It is commonly used to evaluate mechanical properties, especially fatigue behavior under stress.
    Effectiveness Analysis: The cyclic bending test has little direct relationship with improving electrical properties. While it can reflect thek
    Conclusion: Ineffective. The cyclic bending test is mainly used to evaluate the mechanical properties of materials and cannot directly improve electrical performance, so it has no direct effect on improving the electrical performance of thermoelectric materials. The output format is a list. Note that the elements in the list are of string type.
    ###Effective### ["Cryogenic Orientation"]###End Effective### 
    ###Ineffective### ["Cyclic Bending Test"]###End Ineffective###
    ###Uncertain### ["PVA (Polyvinyl Alcohol)", "Elemental Analysis"]###End Uncertain###
    If there are any empty categories for effective, ineffective, or uncertain, please output empty lists[].for example ###Effective### []###End Effective### 
    Output format:
    Thought Process
    ###Effective### []###End Effective###
    ###Ineffective### []###End Ineffective###
    ###Uncertain### []###End Uncertain###
    Now, please gradually analyze the chemical points provided below, according to the format,The output format is a list. Note that the elements in the list are of string type :
    The specific scientific problem is {research_question}
    The chemical points to analyze are {batch}                  
    """
    return prompt

def extract_lists_from_text(text):
    """
    Use regular expressions to extract the list content within the tags from the input text.

    :param text: The input text string
    :return: A tuple containing three lists (effective_list, ineffective_list, uncertain_list)

    """
  
    effective_pattern = r"###\s*Effective\s*###\s*(\[.*?\])\s*###\s*End\s+Effective\s*###"
    ineffective_pattern = r"###\s*Ineffective\s*###\s*(\[.*?\])\s*###\s*End\s+Ineffective\s*###"
    uncertain_pattern = r"###\s*Uncertain\s*###\s*(\[.*?\])\s*###\s*End\s+Uncertain\s*###"
    
    # Use regular expressions to search for matching content.
    effective_match = re.search(effective_pattern, text, re.DOTALL)
    ineffective_match = re.search(ineffective_pattern, text, re.DOTALL)
    uncertain_match = re.search(uncertain_pattern, text, re.DOTALL)
    
    # Extract the matched list content.
    effective_list = eval(effective_match.group(1)) if effective_match else None
    ineffective_list = eval(ineffective_match.group(1)) if ineffective_match else None
    uncertain_list = eval(uncertain_match.group(1)) if uncertain_match else None
    
    return effective_list, ineffective_list, uncertain_list
def validate_chemical_classification(feedback, prompt, api_request):

    # print(f"category_assignment\n\n{categories}")
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        effective_list, ineffective_list, uncertain_list = extract_lists_from_text(feedback)
        
        # Check if all three lists are not None.
        if all(lst is not None for lst in [effective_list, ineffective_list, uncertain_list]):
            return effective_list, ineffective_list, uncertain_list 
        print(f"Error: Extracted  chemical_classification is not a valid list. Received:\n\n{effective_list, ineffective_list, uncertain_list}")
        print(f"Error: Extracted chemical_classification is not a valid list. Received:\n\nEffective: {effective_list}\nIneffective: {ineffective_list}\nUncertain: {uncertain_list}")
        prompt += """Please verify and output in the correct list format. Output format:
        Thought Process
        ###Effective### []###End Effective###
        ###Ineffective### []###End Ineffective###
        ###Uncertain### []###End Uncertain###If there are any empty categories for effective, ineffective, or uncertain, please output empty lists[].for example ###Effective### []###End Effective### """
        retry_count += 1
        print(f"Attempt {retry_count} failed. Retrying...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")
        # continue
    print("Critical Error: Could not extract a chemical_classification.")         
    return effective_list, ineffective_list, uncertain_list

def process_chemical_classification (base_dir, index,research_question_filepath,existing_categories):
    file_name = os.path.join(base_dir, f"chemical_classification_{index}.json")
    if os.path.exists(file_name):
        print(f"File {file_name} already exists. Skipping current operation.")
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return  data[0]+data[2]
    
    batch_size = 5
    research_question = read_research_question(research_question_filepath, index)
    total_hypotheses = len(existing_categories)
    effective_list, ineffective_list, uncertain_list = [], [], []
    for i in range(0, total_hypotheses, batch_size):
        # Extract the current batch of hypotheses
        batch = existing_categories[i:i+batch_size]
        prompt = chemical_classification_prompt(research_question, batch)
        print(f"chemical_classification_prompt\n{prompt}")
        feedback = api_request(prompt)
        print(f"\n\nchemical_classification_prompt_feedback\n\n{feedback}")
        effective_list_i, ineffective_list_i, uncertain_list_i = validate_chemical_classification(feedback, prompt, api_request)
        effective_list.extend(effective_list_i)
        ineffective_list.extend(ineffective_list_i)
        uncertain_list.extend(uncertain_list_i)
    chemical_classification = [effective_list, ineffective_list, uncertain_list] 
    file_path = os.path.join(base_dir, f"chemical_classification_{index}_unprocessed.json")
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(chemical_classification, json_file, ensure_ascii=False, indent=4)
    print(f"Chemical classification saved to {file_name}")

    prompt = chemical_uncertain_classification_deal_prompt (research_question, uncertain_list)
    print(f"chemical_uncertain_classification_deal_prompt\n{prompt}")
    feedback = api_request(prompt)
    print(f"\n\nchemical_uncertain_classification_deal_feedback\n\n{feedback}")
    uncertain_list_classification = validate_and_retry_uncertain_classification (feedback, prompt, api_request)
    uncertain_list = update_uncertain_list(uncertain_list_classification, uncertain_list)
    print (f"update_uncertain_list\n{update_uncertain_list}")

    chemical_classification = [effective_list, ineffective_list, uncertain_list] 
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(chemical_classification, json_file, ensure_ascii=False, indent=4)

    return effective_list + uncertain_list


def update_uncertain_list(uncertain_list_classification, uncertain_list):
   # Iterate over the dictionary keys
 
    # Iterate over the dictionary values
    for value_list in uncertain_list_classification.values():
        #  If the value is a list
        if isinstance(value_list, list):
            
            for value in value_list[:]:  # Use value_list[:] to create a copy to avoid modifying the list while traversing
                # If the element is in uncertainty_list, delete it
                if value in uncertain_list:
                    uncertain_list.remove(value)
    for key in uncertain_list_classification.keys():
    # If key is not in uncertainty_list, add
        if key not in uncertain_list:
            uncertain_list.append(key)
    return uncertain_list


def validate_and_retry_uncertain_classification(feedback, prompt, api_request):
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
    max_retries = 10
    # Check if the extracted hypothesis is a valid dictionary
    retry_count = 0
    while retry_count < max_retries:
        uncertain_classification = extract_uncertain_classification(feedback)
        if isinstance(uncertain_classification, dict):
            return uncertain_classification  # 
        else:
            print("Error: Extracted uncertain_classification Could not extract a valid dictionary after retries")
            prompt += """Please ensure the output format is correct.Output Format:###Similar_Classification### {{"category_name": [category_elements]}}###End###"""
           
        retry_count += 1
        # Check if we've exhausted the retry attempts
        print(f"Retry attempt {retry_count} of {max_retries}...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")

       
    print("Critical Error: Could not extract a valid dictionary after retries.")
    return None




def extract_uncertain_classification(feedback):
    """
    Args:
        feedback (str): The input text to search within.

    Returns:
        dict: Extracted dictionary or None if the pattern is not found.
    """
    # Regex to match content between ###Scientific Hypothesis### and ###END Scientific Hypothesis###
    match = re.search(r"###Similar_Classification###.*?(\{.*?\}).*?###End###", feedback, re.DOTALL)
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

def chemical_uncertain_classification_deal_prompt (research_question, uncertain_list):
    prompt =f"""For specific chemical problems, we extract different chemical points from multiple scientific hypotheses. You need to analyze and categorize each point based on the scientific problem, and determine whether they belong to the same category. For example, the chemical points to analyze are [pva, polyvinyl alcohol, PVA gel, guanidine chloride, guanidine salt, guanidinium sulfate]. Based on the names and the similarity of their roles in the scientific problem, pva, polyvinyl alcohol, and PVA gel all belong to the PVA category. Therefore, the output is a dictionary with the category name as the key and the elements of this category as the value: {{"pva": ["pva", "polyvinyl alcohol", "PVA gel"]}}. Meanwhile, guanidine chloride, guanidine salt, and guanidinium sulfate belong to the guanidine salt category, with the output being {{"PVA": ["pva", "polyvinyl alcohol", "PVA gel"],"guanidine salt": ["guanidine chloride", "guanidine salt", "guanidinium sulfate"]}}. 
For groups without similar categories, you can output {{"Cobalt Sulfate": ["Cobalt Sulfate"]}} and classify it as its own category. Category names cannot be "other." Category names should be derived from the name of one of the chemical points within the group. Classification must strictly follow the specified format for output. Chemical points that do not have similar names or the same mechanism of action should not be classified together. The category names must be clear and explicit, and cannot be something like "Other" which lacks specific chemical information.
###Similar_Classification### {{"category_name": [category_elements]}}###End### 
Now, please gradually analyze the chemical points provided below, according to the format:
The specific scientific problem is {research_question}
The chemical points to analyze are {uncertain_list}
"""
    return prompt


def process_classify_num(research_question, hypotheses, cur_category,batch_size):
    existing_categories = [] 
    pro_existing_categories =  []
    # Configuration
    # Process hypotheses in batches
    total_hypotheses = len(hypotheses)
    for i in range(0, total_hypotheses, batch_size):
        # Extract the current batch of hypotheses
        batch = hypotheses[i:i+batch_size]

        # prompt = generate_prompt(research_question, batch, existing_categories)
        prompt = check_class_num_prompt(research_question, batch, existing_categories,cur_category)
        print(prompt)
        feedback = api_request(prompt)
        print(f"\n\nprocess_classify_feedback\n\n{feedback}")
        existing_categories = extract_categories(feedback)
        # print(f"\n\nexisting_categories\n\n{existing_categories}\n\n")
        
        existing_categories = validate_existing_categories(existing_categories, pro_existing_categories, prompt, api_request,max_retries=5)
        pro_existing_categories = existing_categories
        

    return existing_categories       
        
def check_class_num_prompt(research_question: str, hypotheses: List[Tuple[str, str]], existing_categories: List[str],cur_category) -> str:
    prompt = f"""
    We are working on the research question: {research_question}. Currently, we have several research hypothesis candidates for this question, and we would like to know if these candidates can be categorized into specific chemical categories. Each category of hypothesis should share similar chemical key points, such as common materials, experimental parameters,underlying mechanisms or techniques. Could you try your best to classify them?Please identify the chemical key points that constitute the hypothesis, including the basic chemical components, reactions, and mechanistic methods.
    A scientific hypothesis can contain different Chemically Key Points, and each Chemically Key Point is a category. If the experimental materials are different, such as PVA and PEDOT, although both are chemical polymer, their mechanisms of action for specific chemical problems are completely different, and therefore, they cannot be categorized into the same group.Therefore, they fall into two distinct categories. It is important to note that the chemical categories derived from chemical points should not be overly general. They must clearly reflect their significance in addressing chemical problems and have distinct differences from other chemical categories.
    Based on this principle: Let’s think step by step. Firstly, the scientific hypotheses need to be broken down into key points and conclusions. The distinguishing criterion should be that conclusions arise from chemical key points. Subsequent analysis should focus on the key points of the scientific hypotheses without discussing the conclusions. Next, the key chemical points should be assessed in relation to what specific problems they address and whether they share the same mechanism of action. For example, freeze orientation and stretch orientation, both are chemical techniques aimed at constructing oriented structures, and the result of this orientation can effectively correspond to the enhancement of thermoelectric performance. Therefore, they can be classified under "ion orientation."It is crucial to combine chemical knowledge, the analysis of the scientific problem, and the understanding of the scientific hypothesis when classifying. If there is an existing list of classifications, please determine whether these key points belong to it. If they do not, propose a new category. Note that if the substances, methods, or mechanisms in the chemical key points are clearly different, you should propose a new category. Do not force key points that do not belong to an existing category into one just to reduce the number of new categories.
    Below are existing categories\n{existing_categories}\n 
     Currently, the scientific hypothesis key point is {cur_category}. 
     There are too many scientific hypotheses belonging to this key point, and it is necessary to propose more detailed scientific sub-categories for further differentiation. Please pay attention to capturing the core scientific key points that differentiate these scientific hypotheses, aiming to use as few scientific key points as possible to distinguish them. The scientific hypothesis format is (id, scientific hypothesis), as shown below: {hypotheses}. To better distinguish these key points, you need to analyze these scientific hypotheses and propose new, more specific key points, ensuring that no more than 5 scientific hypotheses belong to each new key point. Note that the new key points you propose should clearly reflect the characteristics of these scientific hypotheses and be easily distinguishable. The new points proposed based on scientific hypotheses represent new categories.The specific substance names and mechanisms can be categorized.
    If the scientific key points they contain do not belong to the existing categories, summarize and propose new categories. When proposing new categories, please place them in a new list with the following format. The output format is:###Categories###["Category Name"]###End Categories### If all the key points of the scientific hypothesis belong to the existing categories, output an empty list in the specified format. If no new categories are added, the output format should be:###Categories###[]###End Categories###
    The newly added categories should differ from existing categories in terms of chemical key points, ensuring that the classification is comprehensive while avoiding redundancy.  The newly added categories must clearly reflect their significance in addressing chemical problems and have distinct differences from other chemical categories.
    The newly added categories should is a list, with the format strictly following:["Category Name"]
    The format is as follows:
    ###Categories###["Category Name"]###End Categories### Please think step by step and answer according to the requirements.
    """
    #   Below are the research hypothesis candidates that need to be analyzed.
    # for key, hypothesis in hypotheses:
    #     prompt += f"{key}: {hypothesis}\n"
    return prompt
    
    # prompt = f"""
    # We are working on the research question: {research_question}. Currently, we have several research hypothesis candidates for this question, and we would like to know if these candidates can be categorized into specific chemical categories. Each category of hypothesis should share similar chemical key points, such as common materials, experimental parameters,underlying mechanisms or techniques. Could you try your best to classify them?
    # Classification needs to be tailored to specific scientific problems. For example, if the problem is How to improve the ionic conductivity of a gel, an analysis based on the Chemically Key Points of each scientific hypothesis should be performed. This includes understanding their purpose and extracting commonalities. For instance, in improving ionic transport efficiency in gel materials to enhance conductivity. Some research hypothesis candidates propose using stretch-induced alignment. Others suggest freeze-casting alignment. Others mention electric field-assisted alignment. By analyzing these Chemically Key Points, it is clear that they all aim to create aligned ionic channels to enhance ionic transport efficiency. Thus, they can be grouped into the category of ionic channels. A scientific hypothesis can contain different Chemically Key Points, and each Chemically Key Point is a category. If the experimental materials are different, such as PVA and PEDOT, although both are chemical polymer, their mechanisms of action for specific chemical problems are completely different, and therefore, they cannot be categorized into the same group.Therefore, they fall into two distinct categories. It is important to note that the chemical categories derived from chemical points should not be overly general. They must clearly reflect their significance in addressing chemical problems and have distinct differences from other chemical categories.A scientific hypothesis can contain different Chemically Key Points, and each Chemically Key Point is a category. Therefore, each chemical scientific hypothesis belongs to multiple chemical categories based on different chemical points.
    # Based on this principle: Let’s think step by step. Firstly, the scientific hypotheses need to be broken down into key points and conclusions. The distinguishing criterion should be that conclusions arise from chemical key points. Subsequent analysis should focus on the key points of the scientific hypotheses without discussing the conclusions. Next, the key chemical points should be assessed in relation to what specific problems they address and whether they share the same mechanism of action. Currently, the scientific hypothesis key point is {cur_category}. There are too many scientific hypotheses belonging to this key point, and it is necessary to propose more detailed scientific sub-categories for further differentiation. Please pay attention to capturing the core scientific key points that differentiate these scientific hypotheses, aiming to use as few scientific key points as possible to distinguish them. The scientific hypothesis format is (id, scientific hypothesis), as shown below: {hypotheses}. To better distinguish these key points, you need to analyze these scientific hypotheses and propose new, more specific key points, ensuring that no more than 5 scientific hypotheses belong to each new key point. Note that the new key points you propose should clearly reflect the characteristics of these scientific hypotheses and be easily distinguishable. The new points proposed based on scientific hypotheses represent new categories.
    
    # The newly added categories should is a list, For example, ["Freeze-casting orientation", "Stretching orientation"].The newly added category is an element in the list.with the format strictly following:[Category Name1,Category Name2]
    # The format is as follows:
    # ###Categories###["Category Name"]###End Categories###
    # """
    # return prompt       
        
def process_check_classify_num(research_question, existing_categories, hypotheses, batch_size=1):
    """
    Process scientific hypotheses in batches, classify them into categories, and update current_dict.

    Args:
        research_question (str): The research question to be used for classification.
        existing_categories (list): A list of existing categories.
        hypotheses (list): A list of scientific hypotheses to be categorized.
        batch_size (int): The size of each batch to process.

    Returns:
        dict: The updated current_dict with category assignments.
    """
    current_dict = {}  # Initialize an empty dictionary to store category assignments

    # Process hypotheses in batches
    total_hypotheses = len(hypotheses)
    for i in range(0, total_hypotheses, batch_size):
        # Extract the current batch of hypotheses
        batch = hypotheses[i:i+batch_size]

        # Generate the prompt and get feedback
        prompt = generate_check_prompt(research_question, batch, existing_categories)
        print(f"Processing batch {i//batch_size + 1} of {total_hypotheses // batch_size + 1}")
        print(f"Prompt: {prompt}")

        feedback = api_request(prompt)
        print(f"Feedback: {feedback}")

        # Extract category assignments from feedback
        category_assignment = extract_category_assignment(feedback)
        print(f"Category Assignment: {category_assignment}")

        # Validate the category assignment (with retries if necessary)
        category_assignment = validate_category_assignment(category_assignment, prompt, api_request, max_retries=5)

        # Update current_dict with the category assignments
        for key, values in category_assignment.items():
            if key in current_dict:
                current_dict[key].extend(values)  # Append new values to existing categories
            else:
                current_dict[key] = values  # Add new category if it doesn't exist

    return current_dict  # Return the final dictionary with all category assignments
          
        
        
if __name__ == "__main__":
   filepath = "./gdth_and_gene_hyp_add_id.json"
   research_question_filepath = "./research_question.json"
   output_dir = "./out_cache" #output path
#    batch_size = 10
   process_classify(filepath,research_question_filepath,output_dir)
#    Note that the numbering must be consecutive, and the numbering of new categories should follow the previous sequence.