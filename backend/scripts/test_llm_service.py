from app.config import settings
from app.llm.factory import get_llm_provider
from app.services.llm_service import generate_response


def main():
    print("=" * 60)
    print("LLM ABSTRACTION TEST")
    print("=" * 60)

    print("Configured provider:", settings.llm_provider)

    provider = get_llm_provider()

    print("Provider:", provider.__class__.__name__)

    direct_response = provider.generate(
        prompt="Say hello in one short sentence.",
        system_prompt="You are a concise assistant.",
    )

    print("\nDirect provider response:")
    print(direct_response)

    service_response = generate_response(
        prompt=(
            "USER QUESTION:\n"
            "What should a product manager focus on?\n\n"
            "RELEVANT TRANSCRIPT EVIDENCE:\n"
            "A guest said that product teams should focus on "
            "understanding the customer problem."
        )
    )

    print("\nService response:")
    print(service_response)

    assert direct_response.strip()
    assert service_response.strip()

    print("\n" + "=" * 60)
    print("LLM ABSTRACTION TEST: PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
