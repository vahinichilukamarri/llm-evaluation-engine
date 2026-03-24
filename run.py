from app.services.generator import generate_multiple_responses


def main():
    print("🧠 LLM Evaluation Engine — Phase 1")
    print("----------------------------------")

    prompt = input("\nEnter your prompt: ")

    if not prompt.strip():
        print("❌ Prompt cannot be empty")
        return

    print("\n⏳ Generating responses...\n")

    responses = generate_multiple_responses(prompt)

    print("\n✅ Generated Responses:\n")

    for i, res in enumerate(responses):
        print(f"--- Response {i+1} (Temp={res['temperature']}) ---")
        print(res["response"])
        print()


if __name__ == "__main__":
    main()