from app.services.scorer import calculate_score


def rank_responses(evaluated_results):
    """
    Rank responses based on final score
    """

    ranked = []

    for item in evaluated_results:
        score = calculate_score(item["evaluation"])

        item["final_score"] = score
        ranked.append(item)

    # Sort descending
    ranked.sort(key=lambda x: x["final_score"], reverse=True)

    return ranked


def get_best_response(ranked_results):
    """
    Return best response
    """

    if not ranked_results:
        return None

    return ranked_results[0]