from app.services.llm_service import generate_response


def main():
    context = """
SOURCE 1

Guest: Annie Duke
Episode: This will make you a better decision maker

Transcript excerpt:
When you're making a decision about whether to leave something,
you should be careful about the sunk cost fallacy. The fact that
you have already invested time or effort into something does not
necessarily mean you should continue with it.


SOURCE 2

Guest: Graham Weaver
Episode: How to break out of autopilot and create the life you want

Transcript excerpt:
You should pay attention to whether you are living on autopilot
and whether your current path is actually the life you want.
Sometimes making a change requires recognizing that the current
situation is not aligned with what you want.


SOURCE 3

Guest: Ada Chen Rekhi
Episode: Feeling stuck? Here's how to know when it's time to leave your job

Transcript excerpt:
There are situations where feeling stuck in your job can be a signal
that it is time to consider leaving and finding something that better
fits what you want.
"""

    prompt = f"""
USER QUESTION:

How should I think about leaving my job?

TRANSCRIPT EXCERPTS:

{context}

Answer the question using ONLY the transcript excerpts.

Mention the guests by name when presenting their perspectives.

Do not invent information.

If the excerpts contain useful evidence, summarize that evidence
into a practical answer.
"""

    answer = generate_response(
        prompt=prompt,
        system_prompt=(
            "You are Lenny Growth Assistant. "
            "Use only the provided transcript excerpts. "
            "Do not use general knowledge or invent information."
        ),
    )

    print("\n" + "=" * 70)
    print("DIRECT LLM GROUNDING TEST")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()
