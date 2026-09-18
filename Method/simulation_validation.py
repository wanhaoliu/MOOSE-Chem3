import os
import json
from gpt_api import api_request
from chem_key_simulation_feedback import extract_gdth_hypothesis,get_gene_hypothesis_with_retry,validate_and_retry_hypothesis_score,calculate_y,validate_and_retry_correction_factor


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


def process_hypotheses_key_points(data, index,output_dir):
    # Read the file
    research_question = data[0]
    gdth_hyp_list = data[1]  # Extract gdth_hyp_list
    gene_hyp_list = data[2]  # Extract gene_hyp_list
    process_hypotheses = []
    file_path = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")
    # Check if the file exists
    if os.path.exists(file_path):
    #If the file exists, read the file and obtain `data[0][1]`, which contains "Chemical Key Points".
        with open(file_path, 'r', encoding='utf-8') as f:
            file_path_data = json.load(f)
        gdth_hyp_chem_key = file_path_data[0][1]
    else:
        cur_gdth_hyp = gdth_hyp_list
        prompt = pro_prompt + f"The scientific question in chemistry is:{research_question}"+ f" hypothesis: {cur_gdth_hyp}"
        print(f"gdth_hyp_chem_key_prompt:\n{prompt}")
        gdth_hyp_chem_key = get_gdth_hypothesis_with_retry(prompt, api_request)
        print(f"gdth_hyp_chem_key_feedback:\n{gdth_hyp_chem_key}")
    # print(f"gdth_hyp_chem_key:\n{gdth_hyp_chem_key}")
    gdth_hyp_list.append(gdth_hyp_chem_key)
    # print(f"gdth_hyp_list\n{gdth_hyp_list}")
    process_hypotheses.append(gdth_hyp_list)
    # Only write the gdth_hypothesis once per group
    gene_hyp_group = []
    for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        prompt = pro_prompt + f" hypothesis: {cur_gene_hyp}\n "# [hypothesis]
        print(f"gene_hypothesis_chem_key_prompt:\n{prompt}")
        gene_hypothesis_chem_key = get_gene_hypothesis_with_retry(prompt, api_request)

        print(f"gene_hypothesis_chem_key:\n{gene_hypothesis_chem_key}")
        cur_gene_hyp = [cur_gene_hyp]
        cur_gene_hyp.append(gene_hypothesis_chem_key)
        gene_hyp_group.append(cur_gene_hyp)
    process_hypotheses.append(gene_hyp_group)  
    # output_data = [gdth_hyp_list,gene_hyp_list,gdth_hyp_analyse,gene_hyp_analyse]
    os.makedirs(output_dir, exist_ok=True)
    # file_path = os.path.join(output_dir, f"hypotheses_key_chem_output_{index}.json")

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(process_hypotheses, file, ensure_ascii=False, indent=4)
    print(f"Results and scores have been successfully saved to {file_path}")
    return process_hypotheses    #[[gdth],[[gene],[class,id,hypo,chem_key,[]....]

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
        # print(f"feedback{feedback}")
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
    

def process_hypotheses_score(data, index, research_question,correction_factor,output_dir):
  
    gdth_hyp_list = data[0]  # Extract gdth_hyp_list
    gene_hyp_list = data[1]  # Extract gene_hyp_list
    finally_list = []
    prompt = gdth_hyp_score_prompt + f"The scientific question in chemistry is:{research_question}"+ f"groundtruth scientific hypothesis:{gdth_hyp_list}\n"
    print(f"gdth_hyp_score_prompt:\n{prompt}")
    gdth_hyp_score_feedback = api_request(prompt,temperature = 0)
    print( f"gdth_hyp_score_feedback:\n{gdth_hyp_score_feedback}")
    finally_list.append(gdth_hyp_list)
    
    final_gene = []
    for cur_gene_hyp in gene_hyp_list:
        # Construct the prompt with groundtruth scientific hypothesis and gene hypothesis
        current_gene_hyp_score_prompt = gene_hyp_score_prompt +  f"The scientific question in chemistry is:\n{research_question}"+f"Ground Truth Scientific Hypothesis Key Points Ranking: \n{gdth_hyp_score_feedback}\n generation hypothesis: \n{cur_gene_hyp[1]}"
        print(f"\ngeneration_hypothesis_prompt:\n{current_gene_hyp_score_prompt}")
        # Call the API to get feedback
        gene_hyp_score_feedback = api_request(current_gene_hyp_score_prompt,temperature = 0)
        print(f"\ngene_hyp_score_feedback:\n{gene_hyp_score_feedback}")
            
        # current_classify_check_prompt = classify_check_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{gene_hyp_score_feedback}\n"
        current_classify_check_prompt = classify_check_prompt + f"The scientific question is:\n{research_question}"+f"Ground Truth Scientific Hypothesis Key Points:\n {gdth_hyp_score_feedback}\n Generated Scientific Hypothesis Analysis and Scoring:\n{gene_hyp_score_feedback}"
        print(f"\ncurrent_classify_check_prompt:\n{current_classify_check_prompt}")
        # Call the API to get feedback
        classify_check_feedback = api_request(current_classify_check_prompt,temperature = 0)
        print(f"\nclassify_check_feedback:\n{classify_check_feedback}\n\n")   
                    
        # current_final_score_prompt =  final_score_prompt + f"Generated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        current_final_score_prompt =  final_score_prompt + f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\nGenerated Scientific Hypothesis Analysis and Scoring:{classify_check_feedback}\n"
        print(f"current_final_score_prompt:\n{current_final_score_prompt}")
        # Call the API to get feedback
        final_score_feedback = api_request(current_final_score_prompt,temperature = 0)
        print(f"\n\nfinal_score_feedback:\n\n{ final_score_feedback}")
                    
        # final_score = extract_final_score(final_score_feedback)
        final_score = validate_and_retry_hypothesis_score(final_score_feedback, current_final_score_prompt, api_request)
        print(f"final score :\n {final_score}")
        cur_gene_hyp.append(final_score)
        if correction_factor == 1:
            current_correction_factor_prompt = correction_factor_prompt + f"The scientific question is:{research_question}"+f"Ground Truth Scientific Hypothesis Key Points: {gdth_hyp_score_feedback}\n generation hypothesis: {classify_check_feedback}"
            print(f"current_correction_factor_prompt:\n{current_correction_factor_prompt}")
        # Call the API to get feedback
            current_correction_factor_feedback = api_request(current_correction_factor_prompt,temperature = 0)
            print(f"\n\ncurrent_correction_factor_feedback:\n\n{current_correction_factor_feedback}")
        
            final_correction_factor = validate_and_retry_correction_factor(current_correction_factor_feedback, current_correction_factor_prompt, api_request)
            print(f"final_correction_factor:\n {final_correction_factor}")
            cur_gene_hyp.append(final_correction_factor)
            final_result = final_correction_factor*final_score
        else:
            final_result = final_score

        cur_gene_hyp.append(final_result)
        y = calculate_y(final_result)
        cur_gene_hyp.append(y)
        final_gene.append(cur_gene_hyp)
    finally_list.append(final_gene)
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"hypotheses_final_score_output_{index}.json")

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(finally_list, file, ensure_ascii=False, indent=4)
    # print(f"Results and scores have been successfully saved to {file_path}")
    return file_path
    
def  feedback_score(hypotheses_file,index,correction_factor,output_dir = "."):
    #hypotheses_dir contains the best scientific hypotheses for each category.
    # for index in range(index):
            hypotheses_path = os.path.join(hypotheses_file, f"simulation_validation_{index}.json")
            # output_file = os.path.join(output_dir, f"simulation_output_{index}.json")

            with open(hypotheses_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # print(type(data))
            result = process_hypotheses_key_points(data,index,output_dir)
            # print(result)
            research_question =data[0]
            file_path = process_hypotheses_score(result, index,research_question,correction_factor, output_dir)
            # print(score)
    # return file_path

if __name__ == "__main__":


    # hypotheses_file = f"./Data/simulation_validation/0" 
    # output_dir = "./Data/simulation_validation/output/0"
    # index = 1
    # feedback_score(hypotheses_file,index,output_dir )

    import argparse
    parser = argparse.ArgumentParser(
        description='give integers at the command line')
    parser.add_argument(
        '--num', type=int,help='an integer ')
    
    parser.add_argument(
        "--rep",
        type=int,  
        required=True,
        help="The repetition number for the simulation (e.g., 1, 2)."
    )


    parser.add_argument(
    "--correction_factor",
    type=int,
    default=1,
    choices=[0, 1],  
    help="Whether to use correction factor: 1 to enable (default), 0 to disable."
)
    # parser.add_argument(
    #     '--log', type=argparse.FileType('w'),
    #     help='the file where the sum should be written')
    args = parser.parse_args()



    hypotheses_file = f"./Data/simulation_validation/{args.num}" 
    output_dir = f"./output/output/{args.num}-{args.rep}"
    index = args.num
    correction_factor = args.correction_factor
    feedback_score(hypotheses_file,index,correction_factor,output_dir)

  