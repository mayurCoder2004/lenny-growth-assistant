from app.services.grounding_service import (
    _semantic_score,
    _lexical_relevance,
    _combined_relevance,
)

QUESTION = "How can we improve onboarding and activation?"

CANDIDATES = [
    {
        "name": "Lauryn",
        "content": (
            "We rebuilt Airtable's onboarding flow and focused on "
            "activation, helping users experience value quickly."
        ),
        "title": "Mastering onboarding",
        "distance": 0.50,
    },
    {
        "name": "Sanchan",
        "content": (
            "At a startup you learn how to get started, how to scale "
            "from zero to one, and how to scale a system after product "
            "market fit."
        ),
        "title": "Why Uber's CPO delivers food on weekends",
        "distance": 0.55,
    },
    {
        "name": "Itamar",
        "content": (
            "For onboarding, define the goal, test the onboarding "
            "wizard with users, use prototypes, and run experiments "
            "to build confidence before expanding the implementation."
        ),
        "title": "Becoming evidence-guided",
        "distance": 0.59,
    },
    {
        "name": "Ebi",
        "content": (
            "A product vision needs to be communicated clearly to "
            "the team so everyone understands where the product is going."
        ),
        "title": "Crafting a compelling product vision",
        "distance": 0.58,
    },
]

print("\n" + "=" * 70)
print("GROUNDING SCORE DEBUG")
print("=" * 70)

for candidate in CANDIDATES:
    semantic = _semantic_score(candidate, 0.60)
    lexical = _lexical_relevance(QUESTION, candidate)
    combined = _combined_relevance(semantic, lexical)

    print(f"\n{candidate['name']}")
    print(f"  semantic : {semantic:.4f}")
    print(f"  lexical  : {lexical:.4f}")
    print(f"  combined : {combined:.4f}")
