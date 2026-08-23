from app.services.llm_service import generate_response


def main():
    response = generate_response(
        "Explain product retention in simple words."
    )

    print("\nLLM Response")
    print("------------")
    print(response)


if __name__ == "__main__":
    main()