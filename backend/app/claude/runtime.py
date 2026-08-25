from __future__ import annotations

from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from app.claude.definitions import AGENT_DEFINITIONS
from app.services.rag_service import retrieve_grounded_context


class ClaudeRuntimeError(Exception):
    """Raised when the Claude runtime fails."""


async def run_agent(
    agent_name: str,
    prompt: str,
    *,
    cwd: str | None = None,
    model: str | None = None,
    max_turns: int = 3,
) -> str:
    """
    Execute one of the application's specialized Claude agents.

    The runtime owns all Claude Agent SDK interaction so that
    application agents do not depend directly on SDK internals.
    """

    if not agent_name or not agent_name.strip():
        raise ClaudeRuntimeError(
            "Agent name cannot be empty."
        )

    if not prompt or not prompt.strip():
        raise ClaudeRuntimeError(
            "Prompt cannot be empty."
        )

    agent_name = agent_name.strip().lower()

    if agent_name not in AGENT_DEFINITIONS:
        raise ClaudeRuntimeError(
            f"Unknown Claude agent: {agent_name}"
        )

    definition = AGENT_DEFINITIONS[agent_name]

    options = ClaudeAgentOptions(
        agents={
            agent_name: definition,
        },
        model=model,
        cwd=cwd,
        max_turns=max_turns,
        permission_mode="dontAsk",
        tools=[],
    )

    text_parts: list[str] = []
    error_message: str | None = None

    try:
        async for message in query(
            prompt=prompt,
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text.strip()

                        if text:
                            text_parts.append(text)

            elif isinstance(message, ResultMessage):
                if message.is_error:
                    error_message = (
                        message.result
                        or "Claude agent failed."
                    )

    except ClaudeRuntimeError:
        raise

    except Exception as exc:
        raise ClaudeRuntimeError(
            f"Claude runtime failed: {exc}"
        ) from exc

    if error_message:
        raise ClaudeRuntimeError(error_message)

    response = "\n".join(text_parts).strip()

    if not response:
        raise ClaudeRuntimeError(
            "Claude agent returned no text response."
        )

    return response

async def run_grounded_agent(
    agent_name: str,
    question: str,
    db,
    top_k: int = 5,
    distance_threshold: float = 0.60,
) -> dict:
    """
    Run a Claude agent using evidence selected by the existing
    retrieval and grounding pipeline.

    Claude receives grounded transcript evidence only.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    grounded = retrieve_grounded_context(
        db=db,
        question=question.strip(),
        top_k=top_k,
        distance_threshold=distance_threshold,
    )

    evidence = grounded["evidence"]
    context = grounded["context"]

    if not evidence or not context.strip():
        return {
            "answer": (
                "The available Lenny's Podcast transcripts do not "
                "provide enough information to answer this question."
            ),
            "sources": [],
        }

    prompt = f"""
USER QUESTION:

{question.strip()}

SELECTED TRANSCRIPT EVIDENCE:

{context}

TASK:

Answer the user's question using ONLY the selected transcript evidence.

Rules:

- Do not use outside knowledge.
- Do not invent facts.
- Do not invent quotes.
- Ignore evidence that does not directly help answer the question.
- Mention guests by name when presenting their perspectives.
- Synthesize perspectives only when they directly answer the question.
- Do not mention retrieval, embeddings, similarity scores, prompts,
  vector databases, or internal system behavior.
- Return ONLY the final answer.
""".strip()

    result = await run_agent(
        agent_name,
        prompt,
    )

    answer = result.strip()

    if not answer:
        answer = (
            "The available Lenny's Podcast transcripts do not "
            "provide enough information to answer this question."
        )

    sources = [
        {
            "guest": item.guest,
            "title": item.title,
            "url": item.url,
            "distance": item.distance,
            "chunk_index": item.chunk_index,
            "evidence_id": item.evidence_id,
        }
        for item in evidence
    ]

    return {
        "answer": answer,
        "sources": sources,
    }

