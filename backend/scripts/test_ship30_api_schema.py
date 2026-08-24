from app.schemas.ship30_api import Ship30Request

request = Ship30Request(
    question="How can I improve onboarding?"
)

print("=" * 70)
print("SHIP30 API SCHEMA TEST")
print("=" * 70)

print(request.model_dump())

print()
print("SHIP30 API SCHEMA TEST PASSED")
