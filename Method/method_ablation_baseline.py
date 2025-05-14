import json,os
import argparse
from classify_best import extract_scientific_hypothesis,read_research_question,save_hypotheses,handle_summary_analysis,evaluate_score,validate_summary_analysis
from gpt_api import api_request
from chem_key_simulation_feedback import feedback_score_explore,feedback_score_method
from classify_api import generate_prompt,validate_existing_categories 

def extract_first_elements(result):
    """
    Extract the first element of the value lists in each dictionary from the result list.
    
    Args:
        result (list): A list of dictionaries, where each value is a list.
        
    Returns:
        check_list (list): A list containing the first element of each value list.
    """
    check_list = []
    for item in result:
        for key, value in item.items():
            if isinstance(value, list) and value:  # Ensure value is a list and not empty
                check_list.append(value[0])
    return check_list

    
def extract_gdth_key(index):
    gdth_keys = ['1', '10', '46', '27', '56', '25', '38', '34', '19', '52', '17', '2', '38', '32', '3', '38', '47', '33', '28', '50', '50', '61', '17', '46', '41', '60', '7', '7', '24', '55', '35', '51', '22', '15', '46', '28', '61', '23', '46', '38', '53', '23', '23', '63', '36', '13', '23', '43', '54', '30', '13']

    return  gdth_keys[index]

def get_json_length(file_path):
    """
    This function reads a JSON file from the specified path and returns the length of the JSON data.
    
    Args:
    - file_path (str): The path to the JSON file.
    
    Returns:
    - int: The length of the JSON data (number of elements in the JSON object).
    """
    try:
        # Open the file and load the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Return the length of the JSON data
        return len(data)
    
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def read_json_by_batch(filepath, index, batch_size=10):
    """
    Read data from a JSON file in batches
    
    Args:
        filepath (str): Path to the JSON file
        batch_size (int): Number of key-value pairs to read per batch, defaults to 10
    
    Yields:
        dict: Dictionary of key-value pairs for each batch
    """
    try:
        # Read the entire JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("Data[{}]:".format(index),[key for key in data[1][index]])
        # Check if data[1] is a dictionary
        if not isinstance(data[1][index], dict):
            raise ValueError("data[1][index] is not a dictionary type")
            
        # Get all key-value pairs from data[1]
        items = list(data[1][index].items())
        total_items = len(items)
        
        # Process in batches
        for start_idx in range(0, total_items, batch_size):
            end_idx = min(start_idx + batch_size, total_items)
            batch_dict = dict(items[start_idx:end_idx])
            yield batch_dict
            
    except FileNotFoundError:
        print(f"Error: File {filepath} does not exist")
    except json.JSONDecodeError:
        print(f"Error: File {filepath} is not a valid JSON format")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def choose_hypothesis_prompt(research_question: str, hypotheses) -> str:
    """
    Generates the prompt for Select the scientific hypothesis based on the research question, hypotheses.
    """
    prompt = f"""
You are a chemistry expert tasked with analyzing the chemical research question: '{research_question}'. 
The available scientific hypotheses are provided as a dictionary in the following format: {{id: scientific hypothesis, id: scientific hypothesis}}, where each key-value pair represents a hypothesis. Specifically:
- Each key is a unique ID (a string, e.g., "0", "1", "2") that uniquely identifies a scientific hypothesis.
- Each value is the full text of the corresponding scientific hypothesis, as a string.
The candidate hypotheses dictionary is: {hypotheses}

Your task is to:
Select the hypothesis you consider most effective and likely to resolve the question.

Output your selection as a dictionary where:
- The key is the hypothesis ID (e.g., "4", "27"), a string, used directly as the dictionary key.
- The value is the full text of the selected scientific hypothesis, as a string.

Format your output exactly as follows:
###Scientific Hypothesis###
{{"id": "hypothesis text"}}
###End###

For example:
###Scientific Hypothesis###
{{"65": "By integrating multi-responsive surfactant-modified droplets with 3D hierarchical graphene-MOF (ZIF-8) structures and employing novel redox couples such as V²⁺/V³⁺ derived from vanadium oxides, we intend to achieve a synergistic improvement in ion transport efficiency and electrode performance in N-type quasi-solid-state thermocells."}}
###End###

Notes:
- The input hypotheses are provided in the format {{id: scientific hypothesis, id: scientific hypothesis}}, where each ID (e.g., "0", "1", "2", etc.) is a unique string key corresponding to one hypothesis.
- When selecting the best hypothesis, you must use the exact ID from the input dictionary as the key in your output dictionary.
- The output dictionary must use the hypothesis ID as the key and the value must be the full hypothesis text.
- Ensure the output matches the example format precisely, with no additional text or deviations outside the ###Scientific Hypothesis### and ###End### markers.
"""
    return prompt


def generate_experiment_prompt(score_path, num_entries):
    """
    Read experiment data from score_path file and generate experiment_prompt based on num_entries parameter.
    
    Parameters:
        score_path (str): Path to the JSON file
        num_entries (int or str): Number of entries to read, supports 1, 5, 10, or "all"
    
    Returns:
        str: Formatted experiment_prompt string
    """
    # Read JSON file
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get experiment data
    experiment_data = data[1]
    
    # Check data length
    total_entries = len(experiment_data)
    if total_entries == 0:
        return "No experiment data available."
    
    # Determine number of entries to read based on num_entries
    if num_entries == "all":
        entries_to_read = total_entries
    else:
            try:
                entries_to_read = int(num_entries)
                if entries_to_read <= 0:
                    raise ValueError("num_entries must be a positive integer")
                entries_to_read = min(entries_to_read, total_entries)  # Prevent reading beyond data length
            except (ValueError, TypeError):
                raise ValueError("num_entries must be a positive integer or 'all'")
    
    # Read the specified number of latest entries
    selected_data = experiment_data[-entries_to_read:]
    
    # Construct experiment_prompt
    prompt_lines = []
    # for entry in selected_data:
    for idx, entry in enumerate(selected_data, start=1):  # Start numbering from 1
        # hypothesis_id = entry[1]  # Assume ID is at index 1
        hypothesis_text = entry[2]  # Assume hypothesis text is at index 2
        score = entry[5]  # Assume score is at index 5
        prompt_lines.append(f"We conducted the Experiment {idx} as follows:")
        prompt_lines.append(
            f"Hypothesis: {hypothesis_text}, "
            f"Score of the experimental feedback: {score}"
        )
    
    # Join all experiment data into a single string
    experiment_prompt = "\n".join(prompt_lines)
    
    return experiment_prompt




def choose_hypothesis_feedback_prompt(research_question, hypotheses,score_path,num_entries) -> str:
    """
    Generates the prompt for Select the scientific hypothesis based on the research question, hypotheses.
    """
    # with open(score_path, 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    # experiment_data = data[1]
    # experiment_prompt = f"We conducted the Experiment as follows: id of Scientific Hypothesis : {experiment_data[-1][1]}  Hypothesis is {experiment_data[-1][2]},The score of the experimental feedback:{experiment_data[-1][5]}"
    experiment_prompt = generate_experiment_prompt(score_path, num_entries)
    prompt = f"""
You are a chemistry expert tasked with analyzing the chemical research question: '{research_question}'. Your goal is to select the best scientific hypothesis from the provided candidate hypotheses dictionary, based on experimental feedback.

We have conducted experiments on these hypotheses and obtained normalized feedback scores, where 1.0 is the highest score and 0.0 is the lowest. The experimental feedback is: {experiment_prompt}.

The available scientific hypotheses are provided in the candidate hypotheses dictionary, formatted as: {{id: scientific hypothesis}}, where:
Each key is a unique ID (a string, e.g., "0", "1", "4") identifying a hypothesis.
Each value is the full text of the corresponding scientific hypothesis, as a string.
The candidate hypotheses dictionary is: {hypotheses}. You must select the hypothesis exclusively from this dictionary.
Your task is to:
Evaluate the experimental feedback scores to determine the most effective hypothesis from the candidate hypotheses dictionary
Select the hypothesis most likely to resolve the research question based on this evaluation.
Output your selection as a dictionary with:

The key being the hypothesis ID (e.g., "4", "27"), a string, taken directly from the candidate hypotheses dictionary.
The value being the full text of the selected scientific hypothesis, as a string.
Format your output exactly as follows:

###Scientific Hypothesis###

{{"id": "hypothesis_text"}}

###End###

For example:

###Scientific Hypothesis###

{{"65": "By integrating multi-responsive surfactant-modified droplets with 3D hierarchical graphene-MOF (ZIF-8) structures and employing novel redox couples such as V²⁺/V³⁺ derived from vanadium oxides, we intend to achieve a synergistic improvement in ion transport efficiency and electrode performance in N-type quasi-solid-state thermocells."}}

###End###

Notes:
Do not select hypotheses that have already been experimented on; you need to choose those that have not been tested. Based on the feedback from conducted experiments, select and output the most effective hypothesis that has not been tested, noting that the candidate hypotheses dictionary contains only untested hypotheses. Please make your selection from the candidate hypotheses dictionary.
The hypothesis must be chosen from the candidate hypotheses dictionary, using the exact ID and text as provided.
Ensure the output dictionary uses the hypothesis ID as the key and the full hypothesis text as the value, with no deviations from the specified format.
Do not include additional text or explanations outside the ###Scientific Hypothesis### and ###End### markers.
"""
    return prompt


# def validate_and_retry_hypothesis(feedback, prompt, api_request):
#     """
#     Validates if the extracted scientific hypothesis is a valid dictionary. Retries a specified number of times if invalid.

#     Args:
#         feedback (str): The input feedback to extract the scientific hypothesis from.
#         prompt (str): The initial prompt used for the API request.
#         api_request (callable): Function to make an API request.
#         max_retries (int): Maximum number of retry attempts to extract a valid hypothesis.

#     Returns:
#         dict: Validated scientific hypothesis dictionary or None if validation fails after retries.
#     """
#     # Extract scientific hypothesis using the provided function
    
#     # print(f"Extracted scientific_hypothesis:\n\n{scientific_hypothesis}")
#     max_retries=10
#     # Check if the extracted hypothesis is a valid dictionary
#     retry_count = 0
#     while retry_count < max_retries:
#         scientific_hypothesis = extract_scientific_hypothesis(feedback)
#         if isinstance(scientific_hypothesis, dict):
#             for key, value in scientific_hypothesis.items():  
#                 if isinstance(value, str):  
                    
#                     id_value = key
#                     if (isinstance(id_value, int) and id_value >= 0) or (isinstance(id_value, str) and id_value.isdigit() and int(id_value) >= 0):
#                         return scientific_hypothesis  
#                     else:
#                         print("Error: Extracted hypothesis is not a valid id of Scientific Hypothesis")
#                         prompt += """Please ensure the output format is correct.Output Format: ###Scientific Hypothesis###{"id of Scientific Hypothesis":"Scientific Hypothesis"}###End###Note: Make sure to correctly output the "id of Scientific Hypothesis"""
#             # return scientific_hypothesis
#         print(f"Error: Extracted hypothesis is not a valid dictionary. Received: {scientific_hypothesis}")
#         print("Retrying API request to ensure valid dictionary output...")
#         # Modify prompt to reinforce that the output must be in dictionary format
#         prompt += """The scientific hypothesis must be in dictionary format. Please ensure the output format is correct. Output Format:###Scientific Hypothesis###{"id of Scientific Hypothesis":"Scientific Hypothesis"}###End###"""
#         # Retry the API request
#         retry_count += 1
#         # Check if we've exhausted the retry attempts
#         print(f"Retry attempt {retry_count} of {max_retries}...")
#         feedback = api_request(prompt)
#         print(f"Retry feedback:\n\n{feedback}")

#         # Try extracting the hypothesis again after retry
#         # scientific_hypothesis = extract_scientific_hypothesis(retry_feedback)
 
#     # If after all retries we still don't have a valid dictionary, return None
#     print("Critical Error: Could not extract a valid dictionary after retries.")
#     return None

def validate_and_retry_hypothesis(feedback, prompt, api_request,filepath,index):
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
    max_retries=20
    # Check if the extracted hypothesis is a valid dictionary
    retry_count = 0
    prompt_pro = prompt
    while retry_count < max_retries:
        scientific_hypothesis = extract_scientific_hypothesis(feedback)
        if isinstance(scientific_hypothesis, dict):
            for key, value in scientific_hypothesis.items():  
                if isinstance(value, str):  
                    id_value = key
                    if (isinstance(id_value, int) and id_value >= 0) or (isinstance(id_value, str) and id_value.isdigit() and int(id_value) >= 0):
                        scientific_hypothesis,max_similarity = check_scientific_hypothesis(filepath,scientific_hypothesis,index)
                        if max_similarity >= 0.7:
                            return scientific_hypothesis 
                        else :
                            print("Error, the scientific hypothesis was not selected from the candidate hypotheses dictionary.")
                            # prompt += f"Your selection of {scientific_hypothesis} from the experimental feedback is incorrect. You must choose only from the candidate hypotheses dictionary."
                            prompt += f"Pay attention not to select hypothesis from the experimental feedback, as they have already conducted experiments. For example, your previous selection of {scientific_hypothesis} from the experimental feedback is incorrect because it has experimental results and does not need further experimentation. You should think based on the hypotheses in the experimental feedback and select from the candidate hypotheses dictionary. The candidate hypotheses dictionary consists entirely of hypotheses that have not been experimented on. You must choose only from the candidate hypotheses dictionary."
                            prompt += """\nYou must select the hypothesis exclusively from candidate hypotheses dictionary,using the exact ID and text provided, with no modifications or external sources, and do not use scientific hypotheses from the experimental feedback for output.\n"""

                    else:
                        print("Error: Extracted hypothesis is not a valid id of Scientific Hypothesis")
                        prompt += """Please ensure the output format is correct. Output Format: ###Scientific Hypothesis###{"id of Scientific Hypothesis":"Scientific Hypothesis"}###End###For example:###Scientific Hypothesis###{"65": "By integrating multi-responsive surfactant-modified droplets with 3D hierarchical and employing novel redox couples."}###End### Make sure to correctly output the "id of Scientific Hypothesis Please ensure the output format is correct\n"""
                    
            # return scientific_hypothesis

        else:
            print(f"Error: Extracted hypothesis is not a valid dictionary. Received: {scientific_hypothesis}")
            print("Retrying API request to ensure valid dictionary output...")
            # Modify prompt to reinforce that the output must be in dictionary format
            prompt += """The scientific hypothesis must be in dictionary format. Please ensure the output format is correct. Output Format:###Scientific Hypothesis###{"id of Scientific Hypothesis":"Scientific Hypothesis"}###End###For example:###Scientific Hypothesis###{"65": "By integrating multi-responsive surfactant-modified droplets with 3D hierarchical and employing novel redox couples."}###End###"""
        # Retry the API request
        retry_count += 1
        # Check if we've exhausted the retry attempts
        print(f"validate_and_retry_hypothesis_prompt\n{prompt}\n")
        print(f"Retry attempt {retry_count} of {max_retries}...")
        feedback = api_request(prompt)
        print(f"Retry feedback:\n\n{feedback}")
        prompt = prompt_pro

        # Try extracting the hypothesis again after retry
        # scientific_hypothesis = extract_scientific_hypothesis(retry_feedback)
 
    # If after all retries we still don't have a valid dictionary, return None
    print("Critical Error: Could not extract a valid dictionary after retries.")
    return None





def transform_hypothesis(scientific_hypothesis,i):
    """
    Transform the scientific hypothesis dictionary into the specified list format.

    Args:
        scientific_hypothesis (dict): The input scientific hypothesis dictionary in the format {"id": "hypothesis"}

    Returns:
        list: The transformed list format
    """
    result = []
    for hyp_id, hyp_text in scientific_hypothesis.items():
        transformed_item = {
            i: [
                hyp_id,
                hyp_text
            ]
        }
        result.append(transformed_item)
    return result


def process_hypotheses_and_update(filepath, hypotheses_file, output_dir, index):
    """
    Process hypotheses file and update original file by removing specified ID key-value pair
    
    Args:
        filepath (str): Path to original JSON file, e.g., "./Data/gdth_and_gene_hyp_add_id_64.json"
        hypotheses_file (str): Path to hypotheses file, e.g., "hypotheses_output_{index}.json"
        output_dir (str): Output directory path
        index (int): File index number
    """
    try:
        # Read hypotheses file
        with open(hypotheses_file, 'r', encoding='utf-8') as f:
            hypotheses_data = json.load(f)
        
        # Check if hypotheses_data is valid and has at least one entry
        if not hypotheses_data or not isinstance(hypotheses_data[0], dict):
            raise ValueError("Invalid format in hypotheses_file: empty or not a list of dictionaries")
        
        # Get the first key-value pair from the first dictionary and extract the ID
        first_item = next(iter(hypotheses_data[0].items()))  # Get first (key, value) tuple
        id_to_remove = first_item[1][0]  # Extract ID from the value list (assuming it's the first element)
        
        # Read original file
        with open(filepath, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Check if original_data[1] is a dictionary
        if not isinstance(original_data[1][index], dict):
            raise ValueError("original_data[1] is not a dictionary")
        
        # Remove the key-value pair with specified ID
        if id_to_remove in original_data[1][index]:
            del original_data[1][index][id_to_remove]
        else:
            print(f"Warning: ID {id_to_remove} not found in original file")
        
        # Construct output filename
        file_name = f"gdth_and_gene_hyp_add_id_64_baseline_{index}.json"
        output_path = os.path.join(output_dir, file_name)
        
        # Save updated data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully updated and saved file to: {output_path}")
        return output_path
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {str(e)}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
    except Exception as e:
        print(f"Error occurred: {str(e)}")


def input_hypotheses(filepath,index,id):
    """
    Reads a batch of hypotheses from the JSON file
    """
    hypotheses = []
    with open(filepath, 'r',encoding='utf-8') as file:
        data = json.load(file)   
    current_data = data[1][index]
    key = str(id)
    hypotheses.append((key, current_data[key]))

    return hypotheses  

def hypo_key_points (filepath,index,output_dir,transformed_result,i,research_question):
    hyp_id = transformed_result[0][i][0]
    # hyp_txt = transformed_result[0][i][1]
    input_hyp = input_hypotheses(filepath,index,hyp_id)
    prompt = generate_prompt(research_question, input_hyp)
    print(f"\n\nkey_points_prompt\n\n{prompt}")
    feedback = api_request(prompt)
    print(f"\n\nprocess_classify_feedback\n\n{feedback}")
    _,chemical_key_points = validate_existing_categories(feedback, prompt, api_request)
    chemical_key_points_list = []
    result_dict = {}
    # hypotheses[0] is tuple
    key = input_hyp[0][0]
    # print(f"key {key}\n\n")
    value = chemical_key_points
    result_dict[key] = value
    # print(result_dict)
    chemical_key_points_list.append(result_dict)

    os.makedirs(output_dir, exist_ok=True)
    key_points_file_path = os.path.join(output_dir, f'key_points_file_{index}.json')
    with open(key_points_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(chemical_key_points_list, json_file, ensure_ascii=False, indent=4)


def experiment_result_summary_analysis_baseline(score_path, research_question, previously_analysis,summary_content,output_dir,index):
    with open(score_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    experiment_data = data[1]
    experiment_prompt = ""
    #The analysis is one step behind the experimental results.
    if len(experiment_data) > 1:
        for i in range(len(experiment_data)-1):
            score_prompt = evaluate_score(experiment_data[i][5])
            experiment_prompt += f"\nWe conducted the Experiment {i+1} as follows: Hypothesis is {experiment_data[i][2]}, Scientific Hypothesis Analysis:{previously_analysis[i]},The score of the experimental feedback:{experiment_data[i][5]}, Preliminary analysis results of the experimental feedback: "+ score_prompt 
            
    else:
        experiment_prompt = "Currently, there is no experimental information."
    last_experiment = experiment_data[-1]
    score_prompt = evaluate_score(last_experiment[5])
   
    num = len(experiment_data)
    new_experiment_prompt = f"\nnew experimental results:Experiment {num}: Hypothesis is {last_experiment[2]} Result is {last_experiment[5]}, Preliminary analysis results of the experimental feedback: "+ score_prompt
    key_points_file_path = os.path.join(output_dir, f'key_points_file_{index}.json')
    with open(key_points_file_path, 'r', encoding='utf-8') as json_file:
        key_points = json.load(json_file)
    gene_hypothesis_chem_key = [value for item in key_points for key, value in item.items() if str(last_experiment[1]) == str(key)]
    
    prompt = f"""You are a chemistry expert tasked with addressing the chemical question: {research_question}. To address this issue, I conducted some experiments on the candidate scientific hypotheses for this scientific question. You need to analyze and summarize(record) the experimental results. Help to identify the chemical key points for solving the chemical problem. The following are the previously experimental results and analysis.\n{experiment_prompt}\n You need to refer to the previous content and focus on analyzing the new experimental results. The new experimental results that need to be analyzed are as follows:{new_experiment_prompt}\nThe key points of the scientific hypothesis are split, and the Role and Function of each key point are as follows:\n{gene_hypothesis_chem_key}
    A complete scientific hypothesis consists of multiple Chemical Key Points. I will provide you with the normalized results of these experiments, where the full score is 1.0, and the lowest score is 0.0. An experimental feedback score below 0.1209 suggests that all the key points are likely ineffective. A score above 0.1209 indicates that some key points may effectively address the scientific problem.The higher the score, the more likely the hypothesis contains a greater number of effective Chemical Key Points. Experiments need to be verified through scientific hypotheses. A complete scientific hypothesis consists of multiple Chemical Key Points. The experimental feedback score is the result of the combined effects of multiple Chemical Key Points. In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result. Therefore, when analyzing the scientific hypothesis, it is necessary to consider whether each Chemical Key Point is effective. When analyzing the effectiveness of key points in new experimental results, priority should be given to considering the scientific hypothesis feedback scores of similar or identical key points from previous experimental results and analysis, making a comprehensive judgment on their effectiveness.This process continuously refines the understanding of the mechanisms of chemical key points, helping to identify the correct key points. Summarize(record) should document the analysis results for each key point in the new experimental results, indicating whether it is likely effective, likely ineffective, or uncertain.
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


def experiment_result_prompt_baseline (summary_content, summary_compilation,score_path):
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
            experiment_prompt += f"\nWe conducted the Experiment {num} as follows: Hypothesis is {experiment_data[i][2]},Result is {experiment_data[i][5]}\nSummary of the single-run experiment:{summary_content[i]}\n\n"
    else:
        experiment_prompt = "Currently, there is no experimental information."
    return  experiment_prompt


def choose_hypothesis_feedback_summary_analysis_prompt(research_question, hypotheses,experiment_prompt) -> str:
    """
    Generates the prompt for Select the scientific hypothesis based on the research question, hypotheses.
    """
    prompt = f"""
You are a chemistry expert tasked with analyzing the chemical research question: '{research_question}'. Your goal is to select the best scientific hypothesis from the provided candidate hypotheses dictionary, based on experimental feedback.

We have conducted experiments on these hypotheses and obtained normalized feedback scores, where 1.0 is the highest score and 0.0 is the lowest.In chemical experiments, if only one Chemical Key Point is effective, the experimental score will also be obtained in the reaction result.The following is the analysis of the experimental feedback on the scientific hypothesis\n {experiment_prompt}\n

The available scientific hypotheses are provided in the candidate hypotheses dictionary, formatted as: {{id: scientific hypothesis, id: scientific hypothesis}}, where:

Each key is a unique ID (a string, e.g., "0", "1", "4") identifying a hypothesis.
Each value is the full text of the corresponding scientific hypothesis, as a string.
The candidate hypotheses dictionary is: {hypotheses}. You must select the hypothesis exclusively from this dictionary.

Your task is to:
You need to consider the chemical key points in each hypothesis of the candidate hypotheses dictionary and, in combination with the experimental feedback, select the hypothesis that contains the most effective chemical key points for feedback.
Evaluate the experimental feedback result to determine the most effective hypothesis from the candidate hypotheses dictionary
Select the hypothesis most likely to resolve the research question based on this evaluation.
Output your selection as a dictionary with:

The key being the hypothesis ID (e.g., "4", "27"), a string, taken directly from the candidate hypotheses dictionary.
The value being the full text of the selected scientific hypothesis, as a string.
Format your output exactly as follows:

###Scientific Hypothesis###

{{"id": "hypothesis text"}}

###End###

For example:

###Scientific Hypothesis###

{{"65": "By integrating multi-responsive surfactant-modified droplets with 3D hierarchical graphene-MOF (ZIF-8) structures and employing novel redox couples such as V²⁺/V³⁺ derived from vanadium oxides, we intend to achieve a synergistic improvement in ion transport efficiency and electrode performance in N-type quasi-solid-state thermocells."}}

###End###

Notes:
Do not select hypotheses that have already been experimented on; you need to choose those that have not been tested. Based on the feedback from conducted experiments, select and output the most effective hypothesis that has not been tested, noting that the candidate hypotheses dictionary contains only untested hypotheses. Please make your selection from the candidate hypotheses dictionary.
The hypothesis must be chosen from the candidate hypotheses dictionary, using the exact ID and text as provided.
Ensure the output dictionary uses the hypothesis ID as the key and the full hypothesis text as the value, with no deviations from the specified format.
Do not include additional text or explanations outside the ###Scientific Hypothesis### and ###End### markers.
"""
    return prompt



def summary_analysis_baseline (index, output_dir,score_path,research_question):
    previously_analysis,summary_content,summary_compilation = handle_summary_analysis(index, output_dir,score_path,research_question )
    summary_analysis_prompt = experiment_result_summary_analysis_baseline(score_path, research_question, previously_analysis,summary_content,output_dir,index)
    print(f"\nexperiment_result_summary_analysis_prompt\n{summary_analysis_prompt}\n")
    feedback = api_request(summary_analysis_prompt)
    print(f"\nexperiment_result_summary_analysis_feedback\n\n{feedback}")
    # summary_analysis = extract_summary_analysis(feedback)
    analysis_content, summary_content = validate_summary_analysis(feedback, summary_analysis_prompt , api_request)
    print(f"\n\nextract analysis \n\n {analysis_content }\n\n extract summary\n\n{summary_content}")
    previously_analysis,summary_content,summary_compilation = handle_summary_analysis(index, output_dir,score_path,research_question, analysis_content, summary_content)
    # experiment_prompt = experiment_result_prompt (summary_content, summary_compilation,score_path)
    experiment_prompt = experiment_result_prompt_baseline (summary_content, summary_compilation,score_path)
    return experiment_prompt

## Function
#  calculate the average score of the four aspects. The score range is [0, 1]
def jaccard_similarity(str1, str2):
    words1 = set(str1.split())
    words2 = set(str2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

# ## Function:
# #   whether an element is in a list with a similarity threshold (if th element has a similarity larger than the threshold with any element in the list, return True)
# def if_element_in_list_with_similarity_threshold(list_elements, element, threshold=0.7):
#     element = element.strip().strip('"').strip()
#     for cur_element in list_elements:
#         cur_element = cur_element.strip().strip('"').strip()
#         if jaccard_similarity(element.lower(), cur_element.lower()) > threshold:
#             return True
#     return False

# Check if scientific hypotheses match the target dictionary in the file.
# If exact match fails, find the most similar text using Jaccard similarity.
def if_element_in_list_with_similarity_threshold(target_dict,hyp_text):
    max_similarity = 0
    most_similar_key = None
    most_similar_text = None
    
    for key, value in target_dict.items():
        cur_element = value.strip().strip('"').strip()
        similarity = jaccard_similarity(hyp_text.lower(), cur_element.lower())
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_key = key
            most_similar_text = value
    
    # Output the most similar entry if similarity exceeds threshold
    if max_similarity > 0.7:  # Adjustable threshold
        print(f"Most similar match for '{hyp_text}'"
            f"\n\n{{'{most_similar_key}': '{most_similar_text}'}}"
            f"\nsimilarity score: {max_similarity:.2f}")
    else:
        print(f"No sufficiently similar text found for '{hyp_text}' "
            f"\n\n{{'{most_similar_key}': '{most_similar_text}'}} "
            f"\nmax similarity: {max_similarity:.2f}")
    return most_similar_key , most_similar_text , max_similarity
    # results[most_similar_key] = most_similar_text



def check_scientific_hypothesis(filepath,scientific_hypothesis,index):
    with open(filepath, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    target_dict = original_data[1][index]
    results = {}  # Store results for all hypotheses
    max_similarity = 0.0
    for hyp_id, hyp_text in scientific_hypothesis.items():
        if hyp_id in target_dict:
                original_text = target_dict[hyp_id]
                if original_text == hyp_text:
                    print(f"Hypothesis ID {hyp_id} matched exactly")
                    results[hyp_id] = hyp_text
                    max_similarity = 1.0
                else:
                    # text[:20]
                    print(f"Hypothesis ID {hyp_id} found but text does not match ")
                    most_similar_key , most_similar_text,max_similarity = if_element_in_list_with_similarity_threshold(target_dict,hyp_text)
                    results[most_similar_key] = most_similar_text
        else:
            # max_similarity = 0
            # most_similar_key = None
            # most_similar_text = None
            
            # for key, value in target_dict.items():
            #     similarity = jaccard_similarity(hyp_text.lower(), value.lower())
            #     if similarity > max_similarity:
            #         max_similarity = similarity
            #         most_similar_key = key
            #         most_similar_text = value
            
            # # Output the most similar entry if similarity exceeds threshold
            # if max_similarity > 0.7:  # Adjustable threshold
            #     print(f"Most similar match for '{hyp_text}': "
            #         f"{{'{most_similar_key}': '{most_similar_text}'}}, "
            #         f"similarity score: {max_similarity:.2f}")
            # else:
            #     print(f"No sufficiently similar text found for '{hyp_text}' "
            #         f"(max similarity: {max_similarity:.2f})")
            most_similar_key , most_similar_text,max_similarity = if_element_in_list_with_similarity_threshold(target_dict,hyp_text)
            results[most_similar_key] = most_similar_text
    return results,max_similarity


def hypothesis_baseline(filepath, research_question_filepath, output_dir, stop_num, baseline, num_entries):

        index = stop_num
        research_question = read_research_question(research_question_filepath, index)
        result = {}
        i = 1
        for hypotheses in read_json_by_batch(filepath, index,batch_size=10):
            # print(batch)
            hypothesis_prompt = choose_hypothesis_prompt(research_question, hypotheses)
            print(f"\nhypothesis_prompt\n\n{hypothesis_prompt}")
            feedback = api_request(hypothesis_prompt)
            print(f"\nhypothesis_feedback\n\n{feedback}")
            scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request,filepath,index)
            if scientific_hypothesis:
                # scientific_hypothesis = check_scientific_hypothesis(filepath,scientific_hypothesis,index)
                result.update(scientific_hypothesis)
                # result.append(scientific_hypothesis)

        hypothesis_prompt = choose_hypothesis_prompt(research_question, result)
        print(f"\nhypothesis_prompt\n\n{hypothesis_prompt}")
        feedback = api_request(hypothesis_prompt)
        print(f"hypothesis_feedback\n\n{feedback}")
        scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request,filepath,index)
        if scientific_hypothesis:
            # scientific_hypothesis = check_scientific_hypothesis(filepath,scientific_hypothesis,index)
            transformed_result = transform_hypothesis(scientific_hypothesis,i)
            hypotheses_file = save_hypotheses(transformed_result,index,output_dir)

        score_path = feedback_score_explore(filepath, hypotheses_file, index,research_question_filepath, output_dir)
        if baseline == 1:  
            hypo_key_points (filepath,index,output_dir,transformed_result,i,research_question)
        last_key = extract_gdth_key(index)
        print(f"last_key\n\n{last_key}\n\n")
        check_list = extract_first_elements(transformed_result)
        number = get_json_length(hypotheses_file)
        if last_key in check_list:
            print(f"***The experiment has currently been conducted {number} times***")
            print(f"The key '{last_key}' is found in the check_list. Breaking the loop.")
            print(f"---------------------{i}--------------------------\n\n find gdth hypothesis\n\n")
            return 0
      
        while True:
            i+=1
            # Remove the IDs that have been tested.
            filepath = process_hypotheses_and_update(filepath, hypotheses_file, output_dir, index)
            result_feedback = {}
            # If baseline == 1, analyze and summarize the results of the experiments conducted.
            if baseline == 1:
                    experiment_prompt = summary_analysis_baseline (index, output_dir,score_path,research_question)
            for hypotheses in read_json_by_batch(filepath, index,batch_size=10):
                if baseline == 0:
                    hypothesis_prompt = choose_hypothesis_feedback_prompt(research_question, hypotheses,score_path, num_entries) 
                if baseline == 1:
                    # experiment_prompt = summary_analysis_baseline (index, output_dir,score_path,research_question)
                    hypothesis_prompt = choose_hypothesis_feedback_summary_analysis_prompt(research_question, hypotheses,experiment_prompt)
                print(f"\nhypothesis_feedback_prompt\n\n{hypothesis_prompt}")
                feedback = api_request(hypothesis_prompt)
                print(f"\nhypothesis_feedback\n\n{feedback}")
                scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request,filepath,index)
                if scientific_hypothesis:
                    # scientific_hypothesis = check_scientific_hypothesis(filepath,scientific_hypothesis,index)
                    result_feedback.update(scientific_hypothesis)


            if baseline == 0:
                hypothesis_prompt = choose_hypothesis_feedback_prompt(research_question, result_feedback,score_path, num_entries) 
            if baseline == 1:
                hypothesis_prompt = choose_hypothesis_feedback_summary_analysis_prompt(research_question, result_feedback,experiment_prompt)

            # hypothesis_prompt = choose_hypothesis_feedback_prompt(research_question, result_feedback,score_path,num_entries)
            print(f"\nhypothesis_feedback_prompt\n\n{hypothesis_prompt}")
            feedback = api_request(hypothesis_prompt)
            print(f"\nhypothesis_feedback\n\n{feedback}")
            scientific_hypothesis = validate_and_retry_hypothesis(feedback, hypothesis_prompt, api_request,filepath,index)
            if scientific_hypothesis:
                # scientific_hypothesis = check_scientific_hypothesis(filepath,scientific_hypothesis,index)
                transformed_result = transform_hypothesis(scientific_hypothesis,i)
                hypotheses_file = save_hypotheses(transformed_result,index,output_dir)
            score_path = feedback_score_method(filepath, hypotheses_file, index, score_path,research_question_filepath,output_dir)
            # Key point splitting
            if baseline == 1:  
                hypo_key_points (filepath,index,output_dir,transformed_result,i,research_question)
            number += get_json_length(hypotheses_file)
            print(f"***The experiment has currently been conducted {number} times***")

            print(f"***************************{i}******************************")
            check_list = extract_first_elements(transformed_result)
            if last_key in check_list:
                print(f"The key '{last_key}' is found in the check_list. Breaking the loop.")
                print(f"---------------------{i}--------------------------\n\n find gdth hypothesis\n\n")
                break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='give integers at the command line')
    parser.add_argument(
        '--num', type=int,help='an integer ')
    parser.add_argument(
        '--baseline',
        type=int,
        default=0,
        choices=[0, 1],
        help='baseline value (0, or 1, default is 0)'
    )
    #Parameter 1 without clustering,
    #Parameter 0 without clustering and analysis, only simulated feedback.




    
    parser.add_argument(
            "--num_entries",
            type=str,  # Accept as string to handle both numbers and "all"
            default=0,
            help="Number of entries to read: any positive integer or 'all'"
        )
    # The num_entries parameter represents the number of entries from the feedback experiment results for each trial.
    
    args = parser.parse_args()

    filepath = r"./Data/gdth_and_gene_hyp_add_id_64.json"
    research_question_filepath = r"./Data/background_questions.json"

    # output_dir = r"./output/Output_0414-4o-min/{}".format(args.num) #output path"
    # output_dir = r"./output/Output_0417-noise4-baseline0-all-4o-min/{}".format(args.num) #output path"
    
    output_dir = r"./output/{}".format(args.num) 
    stop_num = args.num
    baseline = args.baseline
    num_entries = args.num_entries

    hypothesis_baseline(filepath, research_question_filepath, output_dir, stop_num,baseline,num_entries)