from classify_api import process_classify,process_check_classify,process_chemical_classification 
from classify_best import choose_hypothesis_explore, choose_hypothesis_method
from chem_key_simulation_feedback import feedback_score_explore, feedback_score_method
import json
# from check_class_num import check_num_class

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
        
def hypothesis_method(filepath, research_question_filepath, output_dir, stop_num):


        index = stop_num
        #process_classify is used to classify scientific hypotheses in batches. The batch size is 1, and the output is in JSON format.
        existing_categories = process_classify(filepath,research_question_filepath,index,output_dir) 
        # print(f"existing_categories{existing_categories}")

        #Analyze and categorize each point based on the scientific problem, and determine whether they belong to one of three categories: effective, ineffective, or uncertain
        existing_categories = process_chemical_classification (output_dir, index,research_question_filepath,existing_categories)
        # print("\n\n\n________________chemical_classification____________________\n\n\n")

        #Analyze which categories of the chemical categories are included in the scientific hypothesis
        process_check_classify(filepath,research_question_filepath,existing_categories,index, output_dir)
        # print("\n\n\n________________process_check_classify____________________\n\n\n")

        #The data_path is where all the classifications and IDs are saved.
        data_path = output_dir
        #{class：[id，hypo]}
        hypotheses_file,result = choose_hypothesis_explore(filepath,research_question_filepath,data_path,index,output_dir )
        #[{class:[id,hypo]},{},{}]
        score_path = feedback_score_explore(filepath, hypotheses_file, index,research_question_filepath, output_dir)
        #[[gdth],[[gene],[class,id,hypo,chem_key,x_score,final_score],[]....]
        # last_key = extract_last_key(filepath, index)
        last_key = extract_gdth_key(index)
        print(f"last_key\n\n{last_key}\n\n")
        check_list = extract_first_elements(result)
        i = 1
        number = get_json_length(hypotheses_file)
        if last_key in check_list:
            print(f"***The experiment has currently been conducted {number} times***")
            print(f"The key '{last_key}' is found in the check_list. Breaking the loop.")
            print(f"---------------------{i}--------------------------\n\n find gdth hypothesis\n\n")
            return 0

        # break
        

        while True:
            result,hypotheses_file = choose_hypothesis_method(filepath,research_question_filepath,data_path,index,score_path,hypotheses_file,output_dir)
       
            score_path = feedback_score_method (filepath,hypotheses_file,index,score_path,research_question_filepath,output_dir)
            number += get_json_length(hypotheses_file)
            print(f"***The experiment has currently been conducted {number} times***")
          
            i+=1
            print(f"***************************{i}******************************")
            check_list = extract_first_elements(result)
            if last_key in check_list:
                print(f"The key '{last_key}' is found in the check_list. Breaking the loop.")
                print(f"---------------------{i}--------------------------\n\n find gdth hypothesis\n\n")
                break
            if i >= 51:
                print(f"ERROR---------------------{i}--------------------------\n\n \n\n")
                break
            
            

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='give integers at the command line')
    parser.add_argument(
        '--num', type=int,help='an integer ')
    
    args = parser.parse_args()

    # filepath = r"./Data/gdth_and_gene_hyp_add_id_truncated_85.json"
    filepath = r"./Data/gdth_and_gene_hyp_add_id_64.json"

    # filepath = r"./Data/processed_10_data.json"
    # research_question_filepath = "E:\desk_mapping\science_discover\main\data\\research_question.json"
    research_question_filepath = r"./Data/background_questions.json"

    

    output_dir = r"./output/{}".format(args.num) #output path"
    stop_num = args.num
    # baseline = args.baseline

    hypothesis_method(filepath, research_question_filepath, output_dir, stop_num)
