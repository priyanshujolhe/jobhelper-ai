def evaluate_skill_metrics(extracted_skills: list, ground_truth_skills: list) -> dict:
    """
    Computes Precision, Recall, and F1-Score for skill extraction.
    """
    extracted_set = {s.lower().strip() for s in extracted_skills}
    truth_set = {s.lower().strip() for s in ground_truth_skills}

    if not truth_set and not extracted_set:
        return {"precision": 1.0, "recall": 1.0, "f1_score": 1.0}

    true_positives = len(extracted_set & truth_set)
    precision = true_positives / len(extracted_set) if extracted_set else 0.0
    recall = true_positives / len(truth_set) if truth_set else 0.0

    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "true_positives": true_positives,
        "false_positives": len(extracted_set - truth_set),
        "false_negatives": len(truth_set - extracted_set),
    }
