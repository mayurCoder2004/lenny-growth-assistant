from app.services.grounding_service import select_grounded_evidence


QUESTION = "How can we improve onboarding and activation?"


CANDIDATES = [
    {
        "source_id": "lauryn-source",
        "content": (
            "We rebuilt Airtable's onboarding flow and focused on "
            "activation, helping users experience value quickly."
        ),
        "chunk_index": 21,
        "title": "Mastering onboarding",
        "guest": "Lauryn Isford",
        "url": None,
        "distance": 0.50,
    },
    {
        "source_id": "sanchan-source",
        "content": (
            "At a startup you learn how to get started, how to scale "
            "from zero to one, and how to scale a system after product "
            "market fit."
        ),
        "chunk_index": 5,
        "title": "Why Uber's CPO delivers food on weekends",
        "guest": "Sanchan Saxena",
        "url": None,
        "distance": 0.55,
    },
    {
        "source_id": "itamar-source",
        "content": (
            "For onboarding, define the goal, test the onboarding "
            "wizard with users, use prototypes, and run experiments "
            "to build confidence before expanding the implementation."
        ),
        "chunk_index": 28,
        "title": "Becoming evidence-guided",
        "guest": "Itamar Gilad",
        "url": None,
        "distance": 0.59,
    },
    {
        "source_id": "vision-source",
        "content": (
            "A product vision needs to be communicated clearly to "
            "the team so everyone understands where the product is going."
        ),
        "chunk_index": 21,
        "title": "Crafting a compelling product vision",
        "guest": "Ebi Atawodi",
        "url": None,
        "distance": 0.58,
    },
]


evidence = select_grounded_evidence(
    question=QUESTION,
    candidates=CANDIDATES,
    max_evidence=5,
)


print("\n" + "=" * 70)
print("GROUNDING TEST")
print("=" * 70)

for item in evidence:
    print(
        f"{item.evidence_id} | "
        f"{item.guest} | "
        f"{item.title}"
    )

selected_guests = {
    item.guest
    for item in evidence
}


assert "Lauryn Isford" in selected_guests, (
    "Relevant Lauryn evidence was incorrectly removed."
)

assert "Itamar Gilad" in selected_guests, (
    "Relevant Itamar evidence was incorrectly removed."
)

assert "Sanchan Saxena" not in selected_guests, (
    "Clearly irrelevant Sanchan evidence was not filtered."
)

assert "Ebi Atawodi" not in selected_guests, (
    "Clearly irrelevant Ebi evidence was not filtered."
)

print("\nGROUNDING TEST PASSED")
