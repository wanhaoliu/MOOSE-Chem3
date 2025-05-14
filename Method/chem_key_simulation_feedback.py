import requests
import json
import re
import math
import os
from gpt_api import api_request
import sys
import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("./Simulator/prompt/chem_key.txt", "r", encoding="utf-8") as file:
    pro_prompt = file.read().strip()
with open("./Simulator/prompt/gdth_hyp_score.txt", "r", encoding="utf-8") as file:
    gdth_hyp_score_prompt = file.read().strip()

with open("./Simulator/prompt/gene_hyp_score.txt", "r", encoding="utf-8") as file:
    gene_hyp_score_prompt = file.read().strip()

with open("./Simulator/prompt/classify_check.txt", "r", encoding="utf-8") as file:
    classify_check_prompt = file.read().strip()

with open("./Simulator/prompt/final_score.txt", "r", encoding="utf-8") as file:
    final_score_prompt = file.read().strip()
with open("./Simulator/prompt/correction_factor.txt", "r", encoding="utf-8") as file:
    correction_factor_prompt = file.read().strip()
# with open("/main/prompt/prompt_two-dimensional/gdth_hyp_score.txt", "r", encoding="utf-8") as file:
#     gdth_hyp_score_prompt = file.read().strip()
# with open("/main/prompt/prompt_two-dimensional/gene_hyp_score.txt", "r", encoding="utf-8") as file:
#     gene_hyp_score_prompt = file.read().strip()  
# with open("/main/prompt/prompt_two-dimensional/classify_check.txt", "r", encoding="utf-8") as file:
#     classify_check_prompt = file.read().strip()  
# with open("/main/prompt/prompt_two-dimensional/final_score.txt", "r", encoding="utf-8") as file:
#     final_score_prompt = file.read().strip()    


# Function to generate verifier's hypothesis
# def gpt(prompt):
#     hypothesis = api_request(prompt)
#     return hypothesis
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


# Function to extract the score from the feedback
def extract_gdth_hypothesis(feedback):
    match = re.search(r"(###Chemical Key Points###.*?###End Results###)", feedback,re.DOTALL)
    return match.group(1).strip() if match else None

def extract_gene_hypothesis(feedback):
    match = re.search(r"(###Chemical Key Points###.*?###End Chemical Key Points###)", feedback,re.DOTALL)
    return match.group(1).strip() if match else None

def get_gdth_hypothesis_with_retry(prompt, api_request):
    """
    Tries to extract Ground Truth Scientific Hypothesis Key with retries.

    Args:
        pro_prompt (str): The initial prompt for the API request.
        cur_gdth_hyp (str): The current Ground Truth Hypothesis.
        api_request (callable): Function to make an API request.
        max_retries (int): The maximum number of retries if extraction fails.

    Returns:
        str: Extracted Ground Truth Hypothesis Key or None if retries exhausted.
    """
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Construct the full prompt by adding the current hypothesis
        feedback = api_request(prompt,temperature = 0)
        print(f"get_gdth_hypothesis_feedback:\n{feedback}")
        # Extract the score       
        gdth_hypothesis_chem_key = extract_gdth_hypothesis(feedback)
        if  gdth_hypothesis_chem_key is not None:
            return gdth_hypothesis_chem_key
        else:
            print("Error: Failed to extract valid Gene Hypothesis Key. Retrying...")
            prompt += """Please strictly follow the output format below. It must include ###Chemical Key Points###, ###End Chemical Key Points###, ###Results###, and ###End Results###. The output format is:###Chemical Key Points###Chemical substance/component/method  Role and Function: Describe the role and function of the substance or method.###End Chemical Key Points###\n###Results###Result:Describe the effects caused by the aforementioned reasons (e.g., performance improvement, efficiency changes).###End Results###"""
            retry_count += 1

    # If the maximum retry limit is reached and extraction failed, return None
    print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")
    return None



def get_gene_hypothesis_with_retry(prompt, api_request):
    """
    Tries to extract Ground Truth Scientific Hypothesis Key with retries.

    Args:
        pro_prompt (str): The initial prompt for the API request.
        cur_gdth_hyp (str): The current Ground Truth Hypothesis.
        api_request (callable): Function to make an API request.
        max_retries (int): The maximum number of retries if extraction fails.

    Returns:
        str: Extracted Ground Truth Hypothesis Key or None if retries exhausted.
    """
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Construct the full prompt by adding the current hypothesis
        feedback = api_request(prompt,temperature = 0)
        # print(f"gene_hypothesis_feedback:\n{feedback}")
        # Extract the score       
        gene_hypothesis_chem_key = extract_gene_hypothesis(feedback)
        if  gene_hypothesis_chem_key is not None:
            return gene_hypothesis_chem_key
        else:
            print("Error: Failed to extract valid Gene Hypothesis Key. Retrying...")
            prompt += """Please strictly follow the output format below. It must include ###Chemical Key Points###, ###End Chemical Key Points###, ###Results###, and ###End Results###. The output format is:###Chemical Key Points###Chemical substance/component/method  Role and Function: Describe the role and function of the substance or method.###End Chemical Key Points###\n###Results###Result:Describe the effects caused by the aforementioned reasons (e.g., performance improvement, efficiency changes).###End Results###"""
            retry_count += 1

    # If the maximum retry limit is reached and extraction failed, return None
    print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")
    return None

def process_hypotheses_key_points(data, index, research_question_filepath,output_dir):
    # Read the file
    research_question = read_research_question(research_question_filepath, index)
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    process_hypotheses = []


    file_path = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")
    # Check if the file exists
    if os.path.exists(file_path):
    #If the file exists, read the file and obtain `data[0][2]`, which contains "Chemical Key Points".
        with open(file_path, 'r', encoding='utf-8') as f:
            file_path_data = json.load(f)
        gdth_hyp_chem_key = file_path_data[0][2]  # [0] Ground Truth Scientific  [1] hypothese [2]key points
    else:
        cur_gdth_hyp = gdth_hyp_list[1]
        prompt = pro_prompt + f"The scientific question is:{research_question}"+ f" hypothesis: {cur_gdth_hyp}\n "
        print(f"gdth_hyp_chem_key_prompt:\n{prompt}")
        gdth_hyp_chem_key = get_gdth_hypothesis_with_retry(prompt, api_request)
    
    
    # feedback = api_request(prompt,)
    # print( f"feedback{feedback}")
    # gdth_hyp_chem_key = extract_gdth_hypothesis(feedback)
    # print(f"gdth_hyp_chem_key:\n{gdth_hyp_chem_key}")
    gdth_hyp_list.append(gdth_hyp_chem_key)
    # print(gdth_hyp_list)
    process_hypotheses.append(gdth_hyp_list)
    # Only write the gdth_hypothesis once per group
    
    gene_hyp_group = []
    for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        
        prompt = pro_prompt +f"The scientific question is:{research_question}"+ f" hypothesis: {cur_gene_hyp[2]}\n "# [key,id,hypothesis]
        print(f"gene_hyp_prompt\n{prompt}")
        gene_hypothesis_chem_key = get_gene_hypothesis_with_retry(prompt, api_request)
        # Call the API to get feedbackres_json
        # feedback = api_request(prompt)
        # print(f"feedback{feedback}")
        # Extract the score       
        # gene_hypothesis_chem_key = extract_gene_hypothesis(feedback)
        # print(f"gene_hypothesis_chem_key:\n{gene_hypothesis_chem_key}")
        cur_gene_hyp.append(gene_hypothesis_chem_key)
        gene_hyp_group.append(cur_gene_hyp)
    process_hypotheses.append(gene_hyp_group)  
    # output_data = [gdth_hyp_list,gene_hyp_list,gdth_hyp_analyse,gene_hyp_analyse]
    os.makedirs(output_dir, exist_ok=True)
    # file_path = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")
    # file_path = f"./hypotheses_key_chem_output_{index}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(process_hypotheses, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return process_hypotheses    #[[gdth],[[gene],[class,id,hypo,chem_key,[]....]
def save_intermediate_results(gene_hyp_group, output_dir, index, i,interval=5):
    """
    定期保存中间结果到文件，以防止数据丢失。
    每隔 `interval` 轮保存一次。

    :param gene_hyp_group: 当前处理的gene hypothesis组
    :param output_dir: 输出目录
    :param index: 当前的索引
    :param interval: 每隔多少轮保存一次
    """
    if i % interval == 0:
        intermediate_file = os.path.join(output_dir, f"intermediate_results_key_points_{index}.json")
        try:
            with open(intermediate_file, "w", encoding="utf-8") as file:
                json.dump(gene_hyp_group, file, ensure_ascii=False, indent=4)
            print(f"Intermediate results saved to {intermediate_file}")
        except Exception as e:
            print(f"Error saving intermediate results: {e}")

def process_class_hypotheses_key_points(data, index, output_dir):
    output_file = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")
    if os.path.exists(output_file):
        print(f"File already exists: {output_file}. Skipping process for index {index}.")
        with open(output_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
        return existing_data
     
    # Read the file
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    process_hypotheses = []
    cur_gdth_hyp = gdth_hyp_list[1]
    prompt = pro_prompt + f" hypothesis: {cur_gdth_hyp}\n "
    gdth_hyp_chem_key = get_gdth_hypothesis_with_retry(prompt, api_request)
    
    # print(prompt)
    # feedback = api_request(prompt,)
    # print( f"feedback{feedback}")
    # gdth_hyp_chem_key = extract_gdth_hypothesis(feedback)
    print(f"gdth_hyp_chem_key:{gdth_hyp_chem_key}")
    gdth_hyp_list.append(gdth_hyp_chem_key)
    print(gdth_hyp_list)
    process_hypotheses.append(gdth_hyp_list)
    # Only write the gdth_hypothesis once per group
    
    gene_hyp_group = []
    intermediate_file = os.path.join(output_dir, f"intermediate_results_key_points_{index}.json")
    
    if os.path.exists(intermediate_file):
        print(f"Found intermediate results, loading from {intermediate_file}")
        try:
            with open(intermediate_file, "r", encoding="utf-8") as file:
                gene_hyp_group = json.load(file)
            print(f"Loaded {len(gene_hyp_group)} items from intermediate results.")
        except Exception as e:
            print(f"Error loading intermediate results: {e}")
    for i, cur_gene_hyp in enumerate(gene_hyp_list):
        # 如果已经处理过，跳过
        if i < len(gene_hyp_group):
            print(f"Skipping already processed gene hypothesis {i}.")
            continue
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        prompt = pro_prompt + f" hypothesis: {cur_gene_hyp[2]}\n "# [key,id,hypothesis]
        print(prompt)
        gene_hypothesis_chem_key = get_gene_hypothesis_with_retry(prompt, api_request)
        # Call the API to get feedbackres_json
        # feedback = api_request(prompt)
        # print(f"feedback{feedback}")
        # Extract the score       
        # gene_hypothesis_chem_key = extract_gene_hypothesis(feedback)
        print(f"gene_hypothesis_chem_key:{gene_hypothesis_chem_key}")
        cur_gene_hyp.append(gene_hypothesis_chem_key)
        gene_hyp_group.append(cur_gene_hyp)
        save_intermediate_results(gene_hyp_group, output_dir, index,i , interval=5)

    process_hypotheses.append(gene_hyp_group)  
    # output_data = [gdth_hyp_list,gene_hyp_list,gdth_hyp_analyse,gene_hyp_analyse]
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")
    # file_path = f"./hypotheses_key_chem_output_{index}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(process_hypotheses, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return process_hypotheses    #[[gdth],[[gene],[class,id,hypo,chem_key,[]....]


def extract_gdth_gene_group(gdth_file,hypotheses_file,index):
    """
    Extract data from gdth_file and hypotheses file based on the index.

    Args:
        gdth_file (str): Path to the gdth file.
        index (int): Index to extract specific data.

    Returns:
        list: A list containing two sublists: data[0][index] key-value pairs and hypotheses values.
    """
    gdth_gene_group = [[],[]]  #[[id,hypo],[class,id,hypo]]

    # Load data from gdth_file
    try:
        with open(gdth_file, 'r',encoding='utf-8') as file:
            data = json.load(file)
            hypothesis_key = f'Ground Truth Scientific Hypothesis {index}'
            # print(data[0][hypothesis_key])
            gdth_gene_group[0] = [hypothesis_key,data[0][hypothesis_key]]
            # print(gdth_gene_group[0]) #['Ground Truth Scientific Hypothesis 9', 'Using mega-electronvolt ultrafast electron diffraction (MeV-UED) combined with resonance-enhanced multiphoton ionization...]
    except FileNotFoundError:
        print(f"File not found: {gdth_file}")
        return gdth_gene_group
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {gdth_file}")
        return gdth_gene_group

    # Load data from hypotheses file
    # hypotheses_file = f"/mnt/petrelfs/repository/simulation_experiment/main/out/hypotheses_output_{index}.json"
    try:
        with open(hypotheses_file, 'r',encoding='utf-8') as file:
            hypotheses_data = json.load(file)
            for hypothesis in hypotheses_data:
                for key, value in hypothesis.items():
                    if isinstance(value, str):
                        #Extract the hypothesis from the data to prevent loss
                        key_h = str(value[0])
                        value[1]=data[1][key_h]
                        value = [value]  # Convert the string to a list
                    gdth_gene_group[1].append([key] + value)
    except FileNotFoundError:
        print(f"File not found: {hypotheses_file}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON in file: {hypotheses_file}")

    return gdth_gene_group

def extract_final_score(feedback):
    ### Final Score ### ... ### End Final Score ###
    match1 = re.search(r"###\s*Final\s*Score\s*###\s*([+-]?\d+(\.\d+)?)\s*(points|Points)?\s*###\s*End\s*Final\s*Score\s*###", feedback, re.DOTALL)
    
    if match1:
        return float(match1.group(1))  

    match2 = re.search(r"Final\s*Score\s*(###)?\s*([\+-]?\d+(\.\d+)?)\s*(points|Points)?\s*(###)?\s*End\s*Final\s*Score", feedback, re.DOTALL)
    
    if match2:
        return float(match2.group(2))  
    return None

def extract_correction_factor(feedback):
    ### Final Score ### ... ### End Final Score ###
    match1 = re.search(r"###\s*Final\s*Correction\s*Factor\s*###\s*([+-]?\d+(\.\d+)?)\s*(points|Points)?\s*###\s*End\s*###", feedback, re.DOTALL)
    
    if match1:
        return float(match1.group(1))  

    match2 = re.search(r"Final\s*Correction\s*Factor\s(###)?\s*([\+-]?\d+(\.\d+)?)\s*(points|Points)?\s*(###)?\s*End", feedback, re.DOTALL)
    
    if match2:
        return float(match2.group(2))  
    return None
# def validate_and_retry_hypothesis_score(final_score_feedback, prompt, api_request):
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
#     final_score = extract_final_score(final_score_feedback)
#     print(f"Extracted scientific_hypothesis_score:\n\n{final_score}")

#     if final_score is None:
#         print("Error: Extracted final score is None. Retrying API request to ensure valid score output...")
#     # Modify prompt to reinforce that the output must strictly follow the format
#         prompt += " The final score must be in the format: ###Final Score### Final Score ###End Final Score###. Please ensure the output format is correct."
#     # Retry the API request
#         retry_feedback = api_request(prompt)
#         print(f"Retry feedback:\n\n{retry_feedback}")
#         # Try extracting the final score again after retry
#         final_score = extract_final_score(retry_feedback)
#     # Validate again after retry
#         if final_score is None:
#             print("Critical Error: Retried API request still returned None. Skipping current iteration due to invalid data format.")
#             return None
#      # Check if the score exceeds the threshold and retry if necessary
#     if final_score > 100:
#         print("Error: Final score exceeds the maximum allowed value (100). Retrying with additional instructions...")
#         # Add additional instructions to the prompt
#         prompt += " Please ensure that the total score does not exceed 100.Please select the highest-scoring generated hypothesis key point within each category of Ground Truth Scientific Hypothesis Key Point and record the score. Avoid duplicating scores."

#         # Retry the API request
#         retry_feedback = api_request(prompt)
#         print(f"Retry feedback after exceeding score threshold:\n\n{retry_feedback}")
#         # Extract the final score again after retry
#         final_score = extract_final_score(retry_feedback)
#         if final_score > 100:
#             print("Critical Error: Retried API request still returned a score exceeding the threshold. Skipping current iteration.")
#             return None
#     return final_score
def validate_and_retry_correction_factor(current_correction_factor_feedback, prompt, api_request):
    retry_count = 0
    max_retries = 10
    while retry_count < max_retries:
        # Extract scientific hypothesis score
        final_correction_factor = extract_correction_factor(current_correction_factor_feedback)
        print(f"Extracted correction_factor:\n\n{final_correction_factor}\n")

        # If final_score is None, retry immediately
        if final_correction_factor is None:
            print("Error: Extracted final output is None. Retrying API request to ensure valid score output...")
            prompt += " The final output must be in the format: ###Final Correction Factor###Final Correction Factor###End### . Please ensure the output format is correct."
            current_correction_factor_feedback = api_request(prompt,temperature = 0)  # Get feedback again
            print(f"Retry feedback:\n\n{current_correction_factor_feedback}")
            retry_count += 1  # Increment retry count
            # continue  # Continue to next iteration to retry
        else:
            return final_correction_factor
   
    print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")     
    return 0




    
def validate_and_retry_hypothesis_score(final_score_feedback, prompt, api_request):
    """
    Validates if the extracted scientific hypothesis is a valid dictionary. Retries if invalid.

    Args:
        final_score_feedback (str): The input feedback to extract the scientific hypothesis from.
        prompt (str): The initial prompt used for the API request.
        api_request (callable): Function to make an API request.
        max_retries (int): The maximum number of retries if final_score is None or exceeds threshold.

    Returns:
        int or None: The validated final score or None if validation fails after retries.
    """
    retry_count = 0
    max_retries = 10
    while retry_count < max_retries:
        # Extract scientific hypothesis score
        final_score = extract_final_score(final_score_feedback)
        print(f"Extracted scientific_hypothesis_score:\n\n{final_score}\n")

        # If final_score is None, retry immediately
        if final_score is None:
            print("Error: Extracted final score is None. Retrying API request to ensure valid score output...")
            prompt += " The final score must be in the format: ###Final Score### Final Score ###End Final Score###. Please ensure the output format is correct."
            final_score_feedback = api_request(prompt,temperature = 0)  # Get feedback again
            print(f"Retry feedback:\n\n{final_score_feedback}")
            retry_count += 1  # Increment retry count
            continue  # Continue to next iteration to retry

        # If final_score <= 100, return valid score
        if final_score <= 100:
            print(f"Valid final score: {final_score}. Proceeding.")
            return final_score

        # If final_score > 100, retry immediately
        print(f"Error: Final score exceeds the maximum allowed value (100). Retrying with additional instructions...")
        prompt += " Please ensure that the total score does not exceed 100. Please select the highest-scoring generated hypothesis key point within each category of Ground Truth Scientific Hypothesis Key Point and record the score. Avoid duplicating scores."
        final_score_feedback = api_request(prompt,temperature = 0)  # Get feedback again
        print(f"Retry feedback after exceeding score threshold:\n\n{final_score_feedback}")
        retry_count += 1  # Increment retry count

        # # Check if max retries reached
        # if retry_count >= max_retries:
        #     print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")
        #     return None
   
    print("Maximum retry limit reached. Skipping current iteration due to invalid data format.")     
    return 0


# def calculate_y(x):
#     try:
#         # Convert x to a float if it is a string
#         x = float(x)-100
#     except ValueError:
#         raise ValueError(f"Invalid input: {x}. x must be a number or a string convertible to a number.")

#     # Calculate y using the formula
#     y = 1 * math.exp(-((x - 0) ** 2) / (2 * 15 ** 2))
#     return y

# def calculate_y(x):
#     try:
#         # Convert x to a float if it is a string
#         x = float(x) - 100
#     except ValueError:
#         raise ValueError(f"Invalid input: {x}. x must be a number or a string convertible to a number.")

#     # Calculate y using the formula
#     # y = 1 * math.exp(-((x - 0) ** 2) / (2 * 15 ** 2))
#     y = 1 * math.exp(-((x - 0) ** 2) / (2000))
    
#     # Format y to be a decimal without scientific notation
#     y = format(y, '.15f')  # Adjust the precision as needed
#     return y


def calculate_y(x):
    try:
        # Convert x to a float if it is a string
        x = float(x)-100
    except ValueError:
        raise ValueError(f"Invalid input: {x}. x must be a number or a string convertible to a number.")

    # Calculate y using the formula
    y = 1 * math.exp(-((x - 0) ** 2) / (2 * 15 ** 2))
#2
    # y_func = lambda x: 1.0 if abs(x) < 1e-6 else max(min(math.exp(-(x**2) / 2000) + 0.1000 * math.exp(-((x - -50.73)**2) / 50) + 0.1000 * math.exp(-((x - -11.54)**2) / 50) + 0.1000 * math.exp(-((x - -76.19)**2) / 50) - 0.1000 * math.exp(-((x - -37.98)**2) / 50) - 0.1000 * math.exp(-((x - -90.13)**2) / 50) + 0.1000 * math.exp(-((x - -38.45)**2) / 50) - 0.1000 * math.exp(-((x - -69.03)**2) / 50) - 0.1000 * math.exp(-((x - -33.89)**2) / 50) + 0.1000 * math.exp(-((x - -76.41)**2) / 50) - 0.1000 * math.exp(-((x - -45.25)**2) / 50) - 0.1000 * math.exp(-((x - -44.26)**2) / 50) - 0.1000 * math.exp(-((x - -18.86)**2) / 50) - 0.1000 * math.exp(-((x - -20.68)**2) / 50) - 0.1000 * math.exp(-((x - -1.28)**2) / 50) + 0.1000 * math.exp(-((x - -17.54)**2) / 50) + 0.1000 * math.exp(-((x - -54.82)**2) / 50) - 0.1000 * math.exp(-((x - -83.39)**2) / 50) + 0.1000 * math.exp(-((x - -62.41)**2) / 50) - 0.1000 * math.exp(-((x - -26.14)**2) / 50) - 0.1000 * math.exp(-((x - -77.46)**2) / 50) + 0.0189 * math.tanh(10 * (x - -10.62)) + 0.0004 * math.tanh(10 * (x - -88.64)) + 0.0016 * math.tanh(10 * (x - -70.97)), 0.98), 0.01)

#3
    # y_func = lambda x: 1.0 if abs(x) < 1e-6 else max(min(math.exp(-(x**2) / 2000) + 0.1000 * math.exp(-((x - -27.17)**2) / 50) + 0.1000 * math.exp(-((x - -77.57)**2) / 50) - 0.1000 * math.exp(-((x - -74.90)**2) / 50) + 0.1000 * math.exp(-((x - -13.26)**2) / 50) - 0.1000 * math.exp(-((x - -74.32)**2) / 50) - 0.1000 * math.exp(-((x - -3.97)**2) / 50) + 0.1000 * math.exp(-((x - -36.71)**2) / 50) + 0.1000 * math.exp(-((x - -84.49)**2) / 50) + 0.1000 * math.exp(-((x - -96.83)**2) / 50) - 0.1000 * math.exp(-((x - -1.47)**2) / 50) + 0.1000 * math.exp(-((x - -20.45)**2) / 50) - 0.1000 * math.exp(-((x - -18.27)**2) / 50) + 0.1000 * math.exp(-((x - -44.58)**2) / 50) - 0.1000 * math.exp(-((x - -49.21)**2) / 50) + 0.1000 * math.exp(-((x - -7.27)**2) / 50) - 0.1000 * math.exp(-((x - -86.47)**2) / 50) + 0.1000 * math.exp(-((x - -75.56)**2) / 50) + 0.1000 * math.exp(-((x - -46.32)**2) / 50) + 0.1000 * math.exp(-((x - -37.27)**2) / 50) + 0.1000 * math.exp(-((x - -7.84)**2) / 50) - 0.1000 * math.exp(-((x - -86.25)**2) / 50) - 0.1000 * math.exp(-((x - -40.18)**2) / 50) + 0.1000 * math.exp(-((x - -62.36)**2) / 50) + 0.1000 * math.exp(-((x - -6.65)**2) / 50) + 0.1000 * math.exp(-((x - -94.06)**2) / 50) + 0.1000 * math.exp(-((x - -93.95)**2) / 50) - 0.1000 * math.exp(-((x - -80.58)**2) / 50) + 0.1000 * math.exp(-((x - -69.63)**2) / 50) - 0.1000 * math.exp(-((x - -48.14)**2) / 50) - 0.1000 * math.exp(-((x - -73.46)**2) / 50) + 0.1000 * math.exp(-((x - -55.65)**2) / 50) + 0.1000 * math.exp(-((x - -96.35)**2) / 50) + 0.1000 * math.exp(-((x - -49.28)**2) / 50) - 0.1000 * math.exp(-((x - -76.41)**2) / 50) - 0.1000 * math.exp(-((x - -6.87)**2) / 50) + 0.1000 * math.exp(-((x - -15.59)**2) / 50) - 0.1000 * math.exp(-((x - -27.78)**2) / 50) + 0.1000 * math.exp(-((x - -16.42)**2) / 50) + 0.1000 * math.exp(-((x - -93.16)**2) / 50) + 0.1000 * math.exp(-((x - -11.10)**2) / 50) + 0.1000 * math.exp(-((x - -80.21)**2) / 50) + 0.1000 * math.exp(-((x - -86.33)**2) / 50) + 0.1000 * math.exp(-((x - -62.67)**2) / 50) + 0.1000 * math.exp(-((x - -98.34)**2) / 50) + 0.1000 * math.exp(-((x - -84.88)**2) / 50) - 0.1000 * math.exp(-((x - -83.44)**2) / 50) + 0.1000 * math.exp(-((x - -62.06)**2) / 50) - 0.1000 * math.exp(-((x - -26.56)**2) / 50) + 0.1000 * math.exp(-((x - -75.56)**2) / 50) - 0.1000 * math.exp(-((x - -42.15)**2) / 50) + 0.1000 * math.exp(-((x - -18.96)**2) / 50) + 0.1000 * math.exp(-((x - -45.41)**2) / 50) + 0.1000 * math.exp(-((x - -70.20)**2) / 50) - 0.1000 * math.exp(-((x - -89.25)**2) / 50) + 0.1000 * math.exp(-((x - -75.08)**2) / 50) - 0.1000 * math.exp(-((x - -49.57)**2) / 50) - 0.1000 * math.exp(-((x - -77.99)**2) / 50) + 0.1000 * math.exp(-((x - -92.78)**2) / 50) + 0.1000 * math.exp(-((x - -31.80)**2) / 50) - 0.1000 * math.exp(-((x - -1.32)**2) / 50) + 0.0072 * math.tanh(10 * (x - -45.17)) + 0.0119 * math.tanh(10 * (x - -32.15)) + 0.0116 * math.tanh(10 * (x - -32.99)) + 0.0141 * math.tanh(10 * (x - -26.40)), 0.98), 0.01)

#1
    # y_func = lambda x: 1.0 if abs(x) < 1e-6 else max(min(math.exp(-(x**2) / 2000) - 0.1000 * math.exp(-((x - -20.51)**2) / 50) + 0.1000 * math.exp(-((x - -29.18)**2) / 50) - 0.1000 * math.exp(-((x - -88.81)**2) / 50) + 0.1000 * math.exp(-((x - -45.21)**2) / 50) + 0.1000 * math.exp(-((x - -63.27)**2) / 50) - 0.1000 * math.exp(-((x - -25.50)**2) / 50), 0.98), 0.01)
    
    
    # Evaluate the lambda function at x
    # y = y_func(x)
    # Format y to be a decimal without scientific notation
    y = format(y, '.15f')  # Adjust the precision as needed
    return y



def process_hypotheses_score(data, index, research_question_filepath,output_dir):
    research_question = read_research_question(research_question_filepath, index)
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    finally_list = []
    prompt = gdth_hyp_score_prompt + f"The scientific question in chemistry is:{research_question}"+ f"groundtruth scientific hypothesis:{gdth_hyp_list[2]}\n"
    gdth_hyp_score_feedback = api_request(prompt,temperature = 0)
    print( f"gdth_hyp_score_feedback:\n{gdth_hyp_score_feedback}")
    finally_list.append(gdth_hyp_list)
    
    final_gene = []
    for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        current_gene_hyp_score_prompt = gene_hyp_score_prompt +  f"The scientific question in chemistry is:{research_question}"+f"Ground Truth Scientific Hypothesis Key Points Ranking: {gdth_hyp_score_feedback}\n generation hypothesis: {cur_gene_hyp[3]}"
        print(f"\ngeneration_hypothesis_prompt:\n{current_gene_hyp_score_prompt}")
        # print(current_gene_hyp_score_prompt)
        # Call the API to get feedback
        gene_hyp_score_feedback = api_request(current_gene_hyp_score_prompt,temperature = 0)
        print(f"gene_hyp_score_feedback:\n{gene_hyp_score_feedback}")
            
        # current_classify_check_prompt = classify_check_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{gene_hyp_score_feedback}\n"
        # print(current_classify_check_prompt)
        current_classify_check_prompt = classify_check_prompt + f"The scientific question is:\n{research_question}"+f"Ground Truth Scientific Hypothesis Key Points:\n {gdth_hyp_score_feedback}\n Generated Scientific Hypothesis Analysis and Scoring:\n{gene_hyp_score_feedback}"
        # print(f"\ncurrent_classify_check_prompt:\n{current_classify_check_prompt}")

        # Call the API to get feedback
        classify_check_feedback = api_request(current_classify_check_prompt,temperature = 0)
        print(f"classify_check_feedback:\n{classify_check_feedback}")   
                    
        # current_final_score_prompt =  final_score_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        # print(prompt)
        current_final_score_prompt =  final_score_prompt + f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\nGenerated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        print(f"current_final_score_prompt:\n{current_final_score_prompt}")
        # Call the API to get feedback
        final_score_feedback = api_request(current_final_score_prompt,temperature = 0)
        print(f"\n\nfinal_score_feedback:\n\n{ final_score_feedback}")
                    
        # final_score = extract_final_score(final_score_feedback)
        final_score = validate_and_retry_hypothesis_score(final_score_feedback, current_final_score_prompt, api_request)
        print(f"final score :\n {final_score}")
        cur_gene_hyp.append(final_score)
        current_correction_factor_prompt = correction_factor_prompt + f"The scientific question is:{research_question}"+f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\n generation hypothesis: {classify_check_feedback}"
        print(f"current_correction_factor_prompt:\n{current_correction_factor_prompt}")

        current_correction_factor_feedback = api_request(current_correction_factor_prompt,temperature = 0)
        print(f"\n\ncurrent_correction_factor_feedback:\n\n{current_correction_factor_feedback}")

        final_correction_factor = validate_and_retry_correction_factor(current_correction_factor_feedback, current_correction_factor_prompt, api_request)
        print(f"final_correction_factor:\n {final_correction_factor}")
        final_result = final_correction_factor*final_score

        y = calculate_y(final_result)
        cur_gene_hyp.append(y)
        final_gene.append(cur_gene_hyp)
    finally_list.append(final_gene)
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_final_score_output_{index}.json")
    # file_path = f"./hypotheses_final_score_output_{index}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(finally_list, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return file_path
    
    
    
def  feedback_score(gdth_file, hypotheses_dir, num_iterations,research_question_filepath,output_dir = "."):
    #hypotheses_dir contains the best scientific hypotheses for each category.
    for index in range(num_iterations):
            os.makedirs(hypotheses_dir, exist_ok=True)
            hypotheses_file = os.path.join(hypotheses_dir, f"hypotheses_output_{index}.json")
            gdth_gene_group = extract_gdth_gene_group(gdth_file, hypotheses_file,index)          
            result = process_hypotheses_key_points(gdth_gene_group,index,research_question_filepath, output_dir)
            # print(result)
            file_path = process_hypotheses_score(result, index,research_question_filepath, output_dir)
            # print(score)
    return file_path

def  feedback_score_explore(gdth_file, hypotheses_file, index, research_question_filepath,output_dir = "."):
    # [[Ground Truth Scientific Hypothesis],[hypotheses]]  [[hypothesis_key,data[0][hypothesis_key],[key_class,id,hypo]]   
    gdth_gene_group = extract_gdth_gene_group(gdth_file, hypotheses_file, index)   
    # Split the chemical key points.  #[[gdth],[[gene],[class,id,hypo,chem_key]....]      
    result = process_hypotheses_key_points(gdth_gene_group, index, research_question_filepath,output_dir)  
    # print(result)    [key(class),id,hypothesis,chem_key]
    #Conduct scoring. #[[gdth],[[gene],[class,id,hypo,chem_key,x_score,final_score],[]....]
    file_path = process_hypotheses_score(result, index, research_question_filepath,output_dir)
    # print(score)
    return file_path   #[[gdth],[[gene],[class,id,hypo,chem_key,x_score,final_score],[]....]
def save_intermediate_score(final_gene, output_dir, index, i,interval=5):
    """
Save intermediate results periodically to prevent data loss. Save once every `interval` rounds.

:param final_gene: The current group of gene hypotheses being processed
:param output_dir: The output directory
:param index: The current index
:param interval: How often to save, in terms of rounds
    """
    if i % interval == 0:
        intermediate_file = os.path.join(output_dir, f"intermediate_results_score_{index}.json")
        try:
            with open(intermediate_file, "w", encoding="utf-8") as file:
                json.dump(final_gene, file, ensure_ascii=False, indent=4)
            print(f"Intermediate results saved to {intermediate_file}")
        except Exception as e:
            print(f"Error saving intermediate results: {e}")

def process_class_hypotheses_score(data, index, output_dir):
    output_file = os.path.join(output_dir, f"hypotheses_final_score_output_{index}.json")
    # Check if the output file already exists, and if so, skip this step
    if os.path.exists(output_file):
        print(f"File already exists: {output_file}. Skipping process for index {index}.")
        return output_file  # Return directly and skip this processing step.
    
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    finally_list = []
    prompt = gdth_hyp_score_prompt + f"groundtruth scientific hypothesis:{gdth_hyp_list[2]}\n"
    gdth_hyp_score_feedback = api_request(prompt,temperature = 0)
    print( f"gdth_hyp_score_feedback:\n{gdth_hyp_score_feedback}")
    finally_list.append(gdth_hyp_list)
    
    final_gene = []
    intermediate_file = os.path.join(output_dir, f"intermediate_results_score_{index}.json")
    # Check if there is an intermediate result file, and if it exists, load it and skip the parts that have already been processed.
    if os.path.exists(intermediate_file):
        print(f"Found intermediate results, loading from {intermediate_file}")
        try:
            with open(intermediate_file, "r", encoding="utf-8") as file:
                final_gene = json.load(file)
            print(f"Loaded {len(final_gene)} items from intermediate results.")
        except Exception as e:
            print(f"Error loading intermediate results: {e}")
    for i, cur_gene_hyp in enumerate(gene_hyp_list):
        # If it has already been processed, skip it
        if i < len(final_gene):
            print(f"Skipping already processed gene hypothesis {i}.")
            continue      
    # for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        current_gene_hyp_score_prompt = gene_hyp_score_prompt + f"Ground Truth Scientific Hypothesis Key Points Ranking: {gdth_hyp_score_feedback}\n generation hypothesis: {cur_gene_hyp[3]}"
        # print(current_gene_hyp_score_prompt)
        # Call the API to get feedback
        gene_hyp_score_feedback = api_request(current_gene_hyp_score_prompt,temperature = 0)
        print(f"gene_hyp_score_feedback:\n{gene_hyp_score_feedback}")
            
        current_classify_check_prompt = classify_check_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{gene_hyp_score_feedback}\n"
        # print(current_classify_check_prompt)
        # Call the API to get feedback
        classify_check_feedback = api_request(current_classify_check_prompt,temperature = 0)
        print(f"classify_check_feedback:\n{classify_check_feedback}")   
                    
        current_final_score_prompt =  final_score_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        # print(prompt)
        # Call the API to get feedback
        final_score_feedback = api_request(current_final_score_prompt,temperature = 0)
        print(f"\n\nfinal_score_feedback:\n\n{ final_score_feedback}")
                    
        # final_score = extract_final_score(final_score_feedback)
        final_score = validate_and_retry_hypothesis_score(final_score_feedback, current_final_score_prompt, api_request)
        print(f"final score :\n {final_score}")
        cur_gene_hyp.append(final_score)
        y = calculate_y(final_score)
        cur_gene_hyp.append(y)
        final_gene.append(cur_gene_hyp)
        save_intermediate_score(final_gene, output_dir, index, i,interval=5)
    finally_list.append(final_gene)
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_final_score_output_{index}.json")
    # file_path = f"./hypotheses_final_score_output_{index}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(finally_list, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return file_path

def  feedback_class_score_explore(gdth_file, hypotheses_file, index, output_dir = "."):
    # [[Ground Truth Scientific Hypothesis],[hypotheses]]  [[hypothesis_key,data[0][hypothesis_key],[key_class,id,hypo]]   
    gdth_gene_group = extract_gdth_gene_group(gdth_file, hypotheses_file, index)   
    #   #[[gdth],[[gene],[class,id,hypo,chem_key]....]      
    result = process_class_hypotheses_key_points(gdth_gene_group, index, output_dir)  
    # print(result)    [key(class),id,hypothesis,chem_key]
    # #[[gdth],[[gene],[class,id,hypo,chem_key,x_score,final_score],[]....]
    file_path = process_class_hypotheses_score(result, index, output_dir)
            # print(score)
    return file_path   #[[gdth],[[gene],[class,id,hypo,chem_key,x_score,final_score],[]....]

def process_hypotheses_score_method (data, index,score_path,research_question_filepath, output_dir):
    with open(score_path, 'r', encoding='utf-8') as f:
        final_data = json.load(f)
    experiment_data = final_data[1]
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    finally_list = []
    research_question = read_research_question(research_question_filepath, index)
    prompt = gdth_hyp_score_prompt +  f"The scientific question in chemistry is:{research_question}" +  f"groundtruth scientific hypothesis:{gdth_hyp_list[2]}\n"
    gdth_hyp_score_feedback = api_request(prompt,temperature = 0)
    print( f"gdth_hyp_score_feedback:\n{gdth_hyp_score_feedback}")
    finally_list.append(gdth_hyp_list)
    
    # final_gene = []
    for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        current_gene_hyp_score_prompt = gene_hyp_score_prompt + f"The scientific question in chemistry is:{research_question}" + f"Ground Truth Scientific Hypothesis Key Points Ranking: {gdth_hyp_score_feedback}\n generation hypothesis: {cur_gene_hyp[3]}"
        # print(current_gene_hyp_score_prompt)
        print(f"\ngeneration_hypothesis_prompt:\n{current_gene_hyp_score_prompt}")
        # Call the API to get feedback
        gene_hyp_score_feedback = api_request(current_gene_hyp_score_prompt,temperature = 0)
        print(f"gene_hyp_score_feedback:\n{gene_hyp_score_feedback}")
        # current_classify_check_prompt = classify_check_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{gene_hyp_score_feedback}\n"
        current_classify_check_prompt = classify_check_prompt + f"The scientific question is:\n{research_question}"+f"Ground Truth Scientific Hypothesis Key Points:\n {gdth_hyp_score_feedback}\n Generated Scientific Hypothesis Analysis and Scoring:\n{gene_hyp_score_feedback}"
        print(f"\ncurrent_classify_check_prompt:\n{current_classify_check_prompt}")
        # print(current_classify_check_prompt)
        # Call the API to get feedback
        classify_check_feedback = api_request(current_classify_check_prompt,temperature = 0)
        print(f"classify_check_feedback:\n{classify_check_feedback}")   
                    
        # current_final_score_prompt =  final_score_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        # # print(prompt)
        # # Call the API to get feedback
        # final_score_feedback = api_request(current_final_score_prompt,temperature = 0)
        # print(f"\n\nfinal_score_feedback:\n\n{ final_score_feedback}")
        current_final_score_prompt =  final_score_prompt + f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\nGenerated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        print(f"current_final_score_prompt:\n{current_final_score_prompt}")    
        final_score_feedback = api_request(current_final_score_prompt,temperature = 0)
        print(f"\n\nfinal_score_feedback:\n\n{ final_score_feedback}")    
        # final_score = extract_final_score(final_score_feedback)
        final_score = validate_and_retry_hypothesis_score(final_score_feedback, current_final_score_prompt, api_request)
        print(f"final score :\n {final_score}")
        cur_gene_hyp.append(final_score)

        current_correction_factor_prompt = correction_factor_prompt + f"\nThe scientific question is:{research_question}\n"+f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\n generation hypothesis: {classify_check_feedback}"
        print(f"current_correction_factor_prompt:\n{current_correction_factor_prompt}")
        # Call the API to get feedback
        current_correction_factor_feedback = api_request(current_correction_factor_prompt,temperature = 0)
        print(f"\n\ncurrent_correction_factor_feedback:\n\n{current_correction_factor_feedback}")

        final_correction_factor = validate_and_retry_correction_factor(current_correction_factor_feedback, current_correction_factor_prompt, api_request)
        print(f"final_correction_factor:\n {final_correction_factor}")
        final_result = final_correction_factor*final_score
        # cur_gene_hyp.append(final_result)
        y = calculate_y(final_result)
        # y = calculate_y(final_score)
        cur_gene_hyp.append(y)
        experiment_data.append(cur_gene_hyp)
        
    #     final_gene.append(cur_gene_hyp)
    # finally_list.append(final_gene)
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_final_score_output_{index}.json")
    # file_path = f"./hypotheses_final_score_output_{index}.json"
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(final_data, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return file_path


def  feedback_score_method(gdth_file, hypotheses_file, index, score_path,research_question_filepath,output_dir = "."):
    #hypotheses_dir contains the best scientific hypotheses for each category.
    # for index in range(num_iterations):
    #         os.makedirs(hypotheses_dir, exist_ok=True)
    #         hypotheses_file = os.path.join(hypotheses_dir, f"hypotheses_output_{index}.json")
    gdth_gene_group = extract_gdth_gene_group(gdth_file, hypotheses_file,index)          
    result = process_hypotheses_key_points(gdth_gene_group,index ,research_question_filepath, output_dir)
    # print(result)
    new_score_path = process_hypotheses_score_method(result, index, score_path, research_question_filepath,output_dir)
    # print(score)
    return new_score_path





if __name__ == "__main__":
    gdth_file = r"./data/gdth_and_gene_hyp_add_id.json"
    hypotheses_file = f"./simulation_experiment/main/out/" 
    num_iterations = 3
    output_dir = "./simulation_experiment/main/out/out_cache/"
    feedback_score(gdth_file,hypotheses_file,num_iterations, output_dir)
    
    """[
    {
        "1. Hierarchical Structures": [
            "19",
            "The development of a flexible thermogalvanic device employing a dual-phase configuration, where a structurally robust solid-state electrolyte integrates with a liquid-phase layer featuring directionally aligned nanochannels formed through thermally controlled guided self-assembly, will enhance both mechanical robustness and Carnot-relative efficiency. Utilizing polyelectrolyte gels for the solid phase and liquid crystalline materials for the nanochannels, the device will achieve superior ion transport and structural integrity. The thermochemical optimization will target thermal gradients between 20-40\u00b0C, using thermogalvanic ions functionalized with guanidine hydrochloride at a concentration of 0.5 M. Rigorous mechanical testing, including cyclic bending and tensile assessments at a frequency of 1 Hz and amplitude of 5 mm, in both ambient and physiological conditions, accompanied by ion transport simulations, will validate the device\u2019s performance. Differentiating from existing technologies, this design introduces hierarchical nanochannel alignment inspired by biomimetic structures for enhanced ionic conduction and fatigue resistance."
        ]
    }
    ]
    """