import os
import json
import argparse
from gpt_api import api_request
from chem_key_simulation_feedback import extract_gdth_hypothesis,get_gene_hypothesis_with_retry,validate_and_retry_hypothesis_score,calculate_y,validate_and_retry_correction_factor

def generate_baseline_prompt_1(research_question: str, gdth_scientific_hypothesis,generated_scientific_hypothesis) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    You are an expert chemist with extensive experience in theoretical and experimental chemistry. You are provided with:
- Research Question: "{research_question}"
- Ground-Truth Hypothesis: "{gdth_scientific_hypothesis}", which scored 100/100 in experimental validation, indicating perfect performance.
- Generated Hypothesis: "{generated_scientific_hypothesis}"

**Task**:
1. Evaluate the generated hypothesis's effectiveness in solving the scientific problem, comparing it directly to the ground-truth hypothesis.
2. Consider:
   - How effectively it addresses the research question relative to the ground-truth.
   - Its ability to achieve comparable experimental outcomes (e.g., predictive power, accuracy, practical impact).
   - Limitations or trade-offs compared to the ground-truth's perfect performance.
3. Assign a score (0-100) based on chemical principles and the ground-truth hypothesis.

**Output Format**:###Final Score### score ###End Final Score### 
For example ###Final Score###  
10.5
###End Final Score###

"""
    return prompt


def generate_baseline_prompt_2(research_question: str, gdth_scientific_hypothesis,generated_scientific_hypothesis) -> str:
    """
    Generates the prompt for clustering based on the research question, hypotheses, and categories.
    """
    prompt = f"""
    You are helping to evaluate the quality of a proposed research hypothesis by a phd student. The groundtruth hypothesis will also be provided to compare. Here we mainly focus on whether the proposed hypothesis has covered the key points of the groundtruth hypothesis. The evaluation criteria is called 'Matched score', which is in a 6-point Likert scale (from 5 to 0). Particularly, \n5 points mean that the proposed hypothesis (1) covers three key points (or covers all the key points) in the groundtruth hypothesis, where every key point is leveraged nearly identically as in the groundtruth hypothesis, and (2) does not contain any extra key point(s) that is redundant, unnecessary, unhelpful, or harmful; \n4 points mean that the proposed hypothesis (1) covers three key points (or covers all the key points) in the groundtruth hypothesis, where every key point is leveraged nearly identically as in the groundtruth hypothesis, and (2) but also contain extra key point(s) that is redundant, unnecessary, unhelpful, or harmful; \n3 points mean that the proposed hypothesis (1) covers two key points in the groundtruth hypothesis, where every key point is leveraged nearly identically as in the groundtruth hypothesis, (2) but does not cover all key points in the groundtruth hypothesis, and (3) might or might not contain extra key points; \n2 points mean that the proposed hypothesis (1) covers one key point in the groundtruth hypothesis, and leverage it nearly identically as in the groundtruth hypothesis, (2) but does not cover all key points in the groundtruth hypothesis, and (3) might or might not contain extra key points; \n1 point means that the proposed hypothesis (1) covers at least one key point in the groundtruth hypothesis, but all the covered key point(s) are used differently as in the groundtruth hypothesis, and (2) might or might not contain extra key points; \n0 point means that the proposed hypothesis does not cover any key point in the groundtruth hypothesis at all. \nUsually total the number of key points a groundtruth hypothesis contain is less than or equal to three. Please note that the total number of key points in the groundtruth hypothesis might be less than three, so that multiple points can be given. E.g., there's only one key point in the groundtruth hypothesis, and the proposed hypothesis covers the one key point nearly identically, it's possible to give 2 points, 4 points, and 5 points. In this case, we should choose score from 4 points and 5 points, depending on the existence and quality of extra key points. 'Leveraging a key point nearly identically as in the groundtruth hypothesis means that in the proposed hypothesis, the same (or very related) concept (key point) is used in a very similar way with a very similar goal compared to the groundtruth hypothesis. \nWhen judging whether an extra key point has apparent flaws, you should use your own knowledge and understanding of that discipline to judge, rather than only relying on the count number of pieces of extra key point to judge. \nPlease evaluate the proposed hypothesis based on the groundtruth hypothesis. \n
    The proposed hypothesis is:{generated_scientific_hypothesis} \n
    The groundtruth hypothesis is: {gdth_scientific_hypothesis}\n
    Please evaluate the proposed hypothesis based on the groundtruth hypothesis, and give a score.Reason: \nMatched score: \n')"

**Output Format**:
Reason:
###Final Score### Matched score ###End Final Score### 
For example ###Final Score###  
2
###End Final Score###

"""
    return prompt

    
def  feedback_score_baseline(hypotheses_file,index,baseline,output_dir = "."):
    #hypotheses_dir contains the best scientific hypotheses for each category.
    hypotheses_path = os.path.join(hypotheses_file, f"simulation_validation_{index}.json")
    # output_file = os.path.join(output_dir, f"simulation_output_{index}.json")

    with open(hypotheses_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # print(type(data))
    # print(result)
    research_question =data[0]
    gdth_hyp_list = data[1]  # Extract gdth_hyp_list
    gene_hyp_list = data[2]  # Extract gene_hyp_list
    final_gene = []
    file_path = os.path.join(output_dir, f"hypotheses_output_result_{index}.json")
    for cur_gene_hyp in gene_hyp_list:
        gdth_scientific_hypothesis = gdth_hyp_list
        generated_scientific_hypothesis = cur_gene_hyp
        if baseline == 1:
            baseline_prompt = generate_baseline_prompt_1(research_question, gdth_scientific_hypothesis,generated_scientific_hypothesis)
        else: #baseline == 2
            baseline_prompt = generate_baseline_prompt_2(research_question, gdth_scientific_hypothesis,generated_scientific_hypothesis)

        print(f"baseline_prompt:\n{baseline_prompt}")
        # Call the API to get feedback
        baseline_feedback = api_request(baseline_prompt,temperature = 0)
        print(f"\n\nbaseline_feedback:\n\n{baseline_feedback}")

        final_score = validate_and_retry_hypothesis_score(baseline_feedback, baseline_prompt, api_request)
        print(f"final score :\n {final_score}")
        cur_gene_hyp = [cur_gene_hyp]
        cur_gene_hyp.append(final_score)
        final_gene.append(cur_gene_hyp)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(final_gene, file, ensure_ascii=False, indent=4)




if __name__ == "__main__":
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
    "--baseline",
    type=int,
    default=1,
    choices=[1, 2], 
    help="Baseline configuration: 1 (default) or 2."
)

    args = parser.parse_args()

    hypotheses_file = f"./Data/simulation_validation/{args.num}" 
    output_dir = f"./output/output-baseline2/{args.num}-{args.rep}"
    index = args.num
    baseline = args.baseline
    feedback_score_baseline(hypotheses_file,index,baseline,output_dir)

  
