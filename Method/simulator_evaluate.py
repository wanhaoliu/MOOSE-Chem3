import os
import argparse
import json
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, mean_absolute_error

class EvaluateSimulator(object):
    def __init__(self, args):
        self.args = args



    def load_real_data(self, data_path, method_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            real_exp_scores = json.load(f)

        with open(method_path, 'r', encoding='utf-8') as f:
            method_exp_scores = json.load(f)

        assert len(real_exp_scores) == 30, f"Expected 30 groups in real data, got {len(real_exp_scores)}"
        assert len(method_exp_scores) == 30, f"Expected 30 groups in method data, got {len(method_exp_scores)}"

        return real_exp_scores, method_exp_scores

    # def load_real_data(self, data_path):
    #     with open(os.path.join(data_path, "gdth_normalized_values.json"), 'r', encoding='utf-8') as f:
    #         real_exp_scores = json.load(f)

    #     # with open(os.path.join(data_path, "method.json"), 'r', encoding='utf-8') as f:
    #     #     method_exp_scores = json.load(f)
    #     # with open(os.path.join(data_path, "method_without_r.json"), 'r', encoding='utf-8') as f:
    #     #     method_exp_scores = json.load(f)
    #     with open(os.path.join(data_path, "baseline1.json"), 'r', encoding='utf-8') as f:
    #         method_exp_scores = json.load(f)

    #     assert len(real_exp_scores) == 30, f"Expected 30 groups in real data, got {len(real_exp_scores)}"
    #     assert len(method_exp_scores) == 30, f"Expected 30 groups in method data, got {len(method_exp_scores)}"

    #     return real_exp_scores, method_exp_scores

    def evaluate(self):
        # real_exp_scores, method_exp_scores = self.load_real_data(self.args.data_path)
        real_exp_scores, method_exp_scores = self.load_real_data(self.args.data_path, self.args.method_path)

        spearman_scores = []
        mse_scores = []
        rmsle_scores = []
        mae_scores = []
        rmse_scores = []
        l1_norm_scores = [] #l1
        perfect_spearman_count = 0

        # Count the number of groups participating in the calculation
        valid_groups = 0

        for group_id in range(30):
            gdth_scores = real_exp_scores[group_id]
            simulator_scores = method_exp_scores[group_id]

            if len(gdth_scores) != len(simulator_scores):
                print(f"Warning: Group {group_id + 1} has mismatched lengths - real: {len(gdth_scores)}, method: {len(simulator_scores)}. Skipping.")
                continue

            if gdth_scores and simulator_scores:
                spearman_coef, _ = spearmanr(gdth_scores, simulator_scores)
                spearman_scores.append(spearman_coef)

                # Statistics for the case where Spearman = 1.0000
                if abs(spearman_coef - 1.0) < 1e-6:  #
                    perfect_spearman_count += 1

                # MSE
                mse = mean_squared_error(gdth_scores, simulator_scores)
                mse_scores.append(mse)

                # RMSLE
                # np.log1p(x)     np.log(1 + x)，Avoid taking the logarithm of 0
                log_true = np.log1p(gdth_scores)
                log_pred = np.log1p(simulator_scores)
                rmsle = np.sqrt(np.mean((log_true - log_pred) ** 2))
                rmsle_scores.append(rmsle)

                # MAE
                mae = mean_absolute_error(gdth_scores, simulator_scores)
                mae_scores.append(mae)


                # RMSE
                rmse = np.sqrt(mse)
                rmse_scores.append(rmse)

                # L1 Norm
                l1_norm = np.sum(np.abs(np.array(gdth_scores) - np.array(simulator_scores)))
                l1_norm_scores.append(l1_norm)

                valid_groups += 1
                
                # print(f"Group {group_id + 1}: Spearman = {spearman_coef:.4f}, MSE = {mse:.4f}")
                print(f"Group {group_id + 1}: Spearman = {spearman_coef:.4f}, MSE = {mse:.4f}, RMSE = {rmse:.4f}, MAE = {mae:.4f}, RMSLE = {rmsle:.4f}, L1 Norm = {l1_norm:.4f}")
            else:
                print(f"Warning: Group {group_id + 1} has no data. Skipping.")

    
        print(f"Total valid groups evaluated: {valid_groups}/30")
        print(f"Number of groups with Spearman = 1.0000: {perfect_spearman_count}/{valid_groups}")

        # Calculate average indicator
        avg_spearman = np.mean(spearman_scores) if spearman_scores else float('nan')
        avg_mse = np.mean(mse_scores) if mse_scores else float('nan')

        # eval_metrics = {
        #     "average_spearman_coefficient": avg_spearman,
        #     "average_mse": avg_mse
        # }
        eval_metrics = {
            "average_spearman_rank_correlation": np.mean(spearman_scores) if spearman_scores else float('nan'),
            "average_mse": np.mean(mse_scores) if mse_scores else float('nan'),
            "average_rmse": np.mean(rmse_scores) if rmse_scores else float('nan'),
            "average_mae": np.mean(mae_scores) if mae_scores else float('nan'),
            "average_rmsle": np.mean(rmsle_scores) if rmsle_scores else float('nan'), # 
            "average_l1_norm": np.mean(l1_norm_scores) if l1_norm_scores else float('nan')

        }

        return eval_metrics

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Evaluate Simulator')
#     parser.add_argument("--data_path", type=str, default="Data/simulation_output/", help="Path to the dataset")
#     args = parser.parse_args()

#     eval_simulator = EvaluateSimulator(args)
#     eval_metrics = eval_simulator.evaluate()

#     print("Evaluation metrics: ", eval_metrics)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate Simulator')
    parser.add_argument("--data_path", type=str, default="Data/real_experiment_normalized_values.json", help="Path to the dataset")
    parser.add_argument("--method_path", type=str, default="./baseline1.json", help="Name of the method data file (e.g., baseline1.json)")
    args = parser.parse_args()

    eval_simulator = EvaluateSimulator(args)
    eval_metrics = eval_simulator.evaluate()

    print("Evaluation metrics: ", eval_metrics)
    