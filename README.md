# ChemsimX: Toward Experiment-Guided Scientific Hypothesis Ranking with Simulated Experimental Feedback

## Overview
ChemsimX is a Python-based tool for **experiment-guided hypothesis ranking** in automated scientific discovery, focused on chemistry. It prioritizes hypotheses using empirical outcomes from prior experiments, outperforming traditional pre-experiment ranking methods.

Key features:
- Simulator modeling hypothesis performance based on similarity to ground truth with noise perturbation.
- Clustering-based ranking using simulated experimental results.
- Datasets: 51 chemical problems (each with 64 hypotheses) and 30 cutting-edge questions (124 hypotheses).
- Outperforms pre-experiment baselines in experiments.

## Quick Start

### Prerequisites
- Linux system (e.g., Ubuntu)
- Python 3.8
- Git
- Conda

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/wanhaoliu/ChemsimX.git
   cd ChemsimX
   ```
2. Create a Conda environment:
   ```bash
   conda create -n chemsimx python=3.8
   ```
3. Activate the environment:
   ```bash
   conda activate chemsimx
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Datasets
- **Chemical Problems**: 51 problems, each with 64 hypotheses, in `Data/gdth_and_gene_hyp_add_id_64.json`. Sourced from top-tier journals (Nature, Science, etc.).
- **Simulation Validation**: 30 cutting-edge chemical questions with 124 hypotheses in `Data/simulation_validation`.
- **Real Experiment Results**: 124 normalized experimental outcomes in `Data/real_experiment_normalized_values.json`.

## Usage

### Hypothesis Ranking
Run hypothesis ranking for one of 51 chemical problems:
```bash
python ./Method/method.py --num <id>
```
- `<id>`: Problem ID (1 to 51).

### Ablation Experiments
Run ablation experiments with baselines:
```bash
python ./Method/method_ablation_baseline.py --num <id> --baseline <0|1> --num_entries all
```
- `<id>`: Problem ID (1 to 51).
- `--baseline`:
  - `0`: Without clustering and analysis, only simulated feedback.
  - `1`: Without clustering.
- `--num_entries all`: Use all feedback experiment results.

### Simulation Validation
Run simulation for 30 chemical questions:
```bash
python ./Method/simulation_validation.py --num <id> --rep <repetitions> --correction_factor 0
```
- `<id>`: Question ID (1 to 30).
- `<repetitions>`: Number of simulation repetitions.
- `--correction_factor 0`: Disable correction (default: 1 to enable).

### Simulation Baseline
Run baseline simulation with Matched Score or Continuous Score:
```bash
python ./Method/simulation_baseline.py --num <id> --rep <repetitions> --baseline <1|2>
```
- `<id>`: Question ID (1 to 30).
- `<repetitions>`: Number of repetitions.
- `--baseline`:
  - `1`: Continuous Score.
  - `2`: Matched Score.

### Simulator Evaluation
Compare simulated results with real experiment outcomes:
```bash
python ./Method/simulator_evaluate.py --data_path Data/real_experiment_normalized_values.json --method_path <method_output>
```
- `--data_path`: Path to 124 real experiment results (default: `Data/real_experiment_normalized_values.json`).
- `<method_output>`: Path to simulated results.

## Dependencies
See `requirements.txt` for details:
- `openai==1.2.0`
- `numpy`
- `scipy`
- `scikit-learn`
- `requests`

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.


