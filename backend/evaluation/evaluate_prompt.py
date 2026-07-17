import json
from pathlib import Path
from backend.prompts.prompt_v1 import build_prompt_v1
from backend.llm import ask_llm


def load_dataset():
    dataset_path = Path(__file__).parent.parent / "dataset" / "page_type_dataset.json"

    with open(dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    dataset = load_dataset()

    print(f"Loaded {len(dataset)} webpages.")

    first_page = dataset[0]

    prompt = build_prompt_v1(first_page)

    prediction = ask_llm(prompt)

    print("\nPrediction:")
    print(prediction)


if __name__ == "__main__":
    main()