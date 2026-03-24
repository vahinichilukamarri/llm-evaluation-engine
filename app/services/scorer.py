def calculate_score(evaluation):
    """
    Calculate final weighted score
    """

    try:
        relevance = evaluation.get("relevance", 0)
        factuality = evaluation.get("factuality", 0)
        completeness = evaluation.get("completeness", 0)
        bias = evaluation.get("bias", 0)

        final_score = (
            0.3 * relevance +
            0.3 * factuality +
            0.2 * completeness +
            0.2 * bias
        )

        return round(final_score, 2)

    except:
        return 0