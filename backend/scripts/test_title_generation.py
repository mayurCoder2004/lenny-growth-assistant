from app.services.chat_service import generate_session_title

tests = [
    "How can I improve activation for my SaaS?",
    "How do I improve product retention?",
    "Write an essay about product growth.",
    "Please help me with user onboarding!",
]

for message in tests:
    print(
        f"{message} -> {generate_session_title(message)}"
    )
