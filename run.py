from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses
from app.services.comparator import rank_responses, get_best_response
from app.services.judge import compare_responses


def get_user_responses():
    """
    Allows user to input multiple responses manually
    """
    responses = []

    try:
        n = int(input("How many responses do you want to enter? "))
    except:
        print("Invalid input")
        return []

    for i in range(n):
        print(f"\nEnter response {i+1}:")
        res = input()

        responses.append({
            "response": res,
            "temperature": "user"
        })

    return responses


def main():
    print("🧠 LLM Evaluation Engine")
    print("------------------------")

    prompt = input("\nEnter your prompt: ")

    if not prompt.strip():
        print("❌ Prompt cannot be empty")
        return

    print("\nChoose mode:")
    print("1. Generate responses")
    print("2. Enter your own responses")

    choice = input("Enter choice: ")

    if choice == "1":
        responses = generate_multiple_responses(prompt)

    elif choice == "2":
        responses = get_user_responses()

    else:
        print("Invalid choice")
        return

    if not responses:
        print("No responses to evaluate")
        return

    print("\n🔍 Evaluating responses...\n")

    evaluated_results = evaluate_multiple_responses(prompt, responses)

    print("\n📊 Ranking responses...\n")

    ranked_results = rank_responses(evaluated_results)
    best = get_best_response(ranked_results)

    print("\n🏆 Ranked Responses:\n")

    for i, item in enumerate(ranked_results):
        print(f"\n--- Rank {i+1} ---")
        print(f"Score: {item['final_score']}")

        print("\nResponse:")
        print(item["response"])

        print("\nEvaluation:")
        print(item["evaluation"])

    print("\n🔥 BEST RESPONSE:\n")
    print(best["response"])
    print(f"\nScore: {best['final_score']}")

    # 🔥 NEW: Comparative Judge
    print("\n🧠 Running comparative judge...\n")

    comparison_result = compare_responses(prompt, responses)

    print("📊 Comparative Ranking (LLM Judge):")

    if isinstance(comparison_result, dict):
        if "ranking" in comparison_result:
            print("\n🏆 Judge Ranking Order:", comparison_result["ranking"])
            print("📝 Reason:", comparison_result.get("reason", "No reason provided"))
        else:
            print(comparison_result)
    else:
        print(comparison_result)


if __name__ == "__main__":
    main()