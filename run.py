from app.services.generator import generate_multiple_responses
from app.services.evaluator import evaluate_multiple_responses


def get_user_responses():
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

    print("\n🔍 Evaluating responses...\n")

    evaluated_results = evaluate_multiple_responses(prompt, responses)

    for i, item in enumerate(evaluated_results):
        print(f"\n--- Response {i+1} ---")
        print(item["response"])

        print("\nEvaluation:")
        print(item["evaluation"])


if __name__ == "__main__":
    main()