"""Collect per-question simulator outputs into the score file that simulator_evaluate.py expects.

simulator_evaluate.py --method_path needs a JSON list with one entry per validation question
(178 by default), aligned with Data/real_experiment_normalized_values.json. Each entry is the list
of simulated scores for that question's hypotheses, in dataset order.

Sources:
  validation  ./output/output/{i}-{rep}/hypotheses_final_score_output_{i}.json
              (simulation_validation.py); uses the normalized feedback y.
  baseline1   ./output/output-baseline1/{i}-{rep}/hypotheses_output_result_{i}.json
              (simulation_baseline.py --baseline 1, 0-100 score, divided by 100).
  baseline2   ./output/output-baseline2/{i}-{rep}/hypotheses_output_result_{i}.json
              (simulation_baseline.py --baseline 2, 0-5 Matched score, divided by 5).

With several --rep values the scores are averaged per hypothesis. Missing or incomplete questions
are written as empty lists, which simulator_evaluate.py skips with a warning.
"""
import argparse
import json
import os

SOURCES = {
    "validation": ("./output/output", "hypotheses_final_score_output_{i}.json", 1.0),
    "baseline1": ("./output/output-baseline1", "hypotheses_output_result_{i}.json", 100.0),
    "baseline2": ("./output/output-baseline2", "hypotheses_output_result_{i}.json", 5.0),
}


def load_scores(source, output_root, index, rep, normalize):
    _, file_pattern, scale = SOURCES[source]
    path = os.path.join(output_root, f"{index}-{rep}", file_pattern.format(i=index))
    if not os.path.exists(path):
        return None, path
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # validation: [gdth, [[hyp, chem_key, final_score, (R), final_result, y], ...]]
    # baseline:   [[hyp, score], ...]
    entries = data[1] if source == "validation" else data
    scores = []
    for entry in entries:
        value = entry[-1]
        scores.append(float(value) if value is not None else 0.0)
    if normalize and scale != 1.0:
        scores = [s / scale for s in scores]
    return scores, path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", choices=sorted(SOURCES), default="validation")
    parser.add_argument("--rep", type=int, nargs="+", default=[1], help="Repetition number(s) to aggregate (averaged).")
    parser.add_argument("--output_root", default=None, help="Override the source's default output directory.")
    parser.add_argument("--num_questions", type=int, default=178)
    parser.add_argument("--no_normalize", action="store_true", help="Keep raw baseline scores instead of scaling to [0, 1].")
    parser.add_argument("--output", required=True, help="Path of the aggregated JSON file to write.")
    args = parser.parse_args()

    output_root = args.output_root or SOURCES[args.source][0]
    groups = []
    missing = 0
    for index in range(args.num_questions):
        per_rep = []
        for rep in args.rep:
            scores, path = load_scores(args.source, output_root, index, rep, not args.no_normalize)
            if scores is None:
                print(f"Warning: missing {path}")
            else:
                per_rep.append(scores)
        if not per_rep or len({len(s) for s in per_rep}) != 1:
            if per_rep:
                print(f"Warning: question {index} has different hypothesis counts across repetitions; skipped.")
            groups.append([])
            missing += 1
            continue
        groups.append([sum(values) / len(values) for values in zip(*per_rep)])

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2)
    print(f"Wrote {len(groups)} groups ({len(groups) - missing} with scores) to {args.output}")


if __name__ == "__main__":
    main()
