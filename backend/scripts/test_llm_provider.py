from app.llm.factory import get_llm_provider


def main():
    provider = get_llm_provider()

    response = provider.generate(
        prompt="Say hello in one short sentence.",
        system_prompt="You are a concise assistant.",
    )

    print("=" * 60)
    print("PROVIDER:", provider.__class__.__name__)
    print("=" * 60)
    print(response)
    print("=" * 60)

    assert response.strip()

    print("Generation test: PASSED")


if __name__ == "__main__":
    main()
