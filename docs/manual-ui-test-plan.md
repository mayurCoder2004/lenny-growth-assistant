# Manual UI Test Plan

## Scope

Use this checklist after starting the backend, frontend, PostgreSQL database, and configured LLM provider. The automated backend tests mock external LLMs; this checklist verifies the browser workflow.

## Checklist

1. Create a new conversation.
   - Click `+ New Chat`.
   - Verify the new conversation appears in the sidebar and becomes active.

2. Send a normal chat question.
   - Select `Chat`.
   - Ask a product-growth question such as `How can I improve product growth?`.
   - Verify a user bubble appears immediately and an assistant response appears after loading.

3. Verify grounded sources appear.
   - Confirm a `Sources` section appears under the assistant response when evidence is found.
   - Open at least one source link and verify it is a safe external link.

4. Ask a follow-up question and verify session context.
   - Send a second message in the same conversation.
   - Refresh or reselect the conversation.
   - Verify both earlier and follow-up messages remain in order.

5. Generate a Ship30 essay.
   - Select `Ship30 Essay`.
   - Ask for an essay grounded in product-growth advice.
   - Verify generation completes without leaving the input permanently disabled.

6. Verify essay formatting.
   - Check that the essay is readable, uses paragraphs/headings where generated, and does not expose internal evidence IDs.

7. Verify Ship30 sources.
   - Confirm the Ship30 assistant message includes source links when grounded evidence is available.
   - Verify source titles or guest names are visible.

8. Generate artifact.
   - Confirm the Ship30 essay request returns an artifact and the artifact area appears below the chat.

9. Verify Artifact Viewer.
   - Confirm the artifact title, type/status area, and generated content render in the artifact viewer.
   - Note: Copy and Export buttons are visual only in the current implementation.

10. Verify responsive UI.
    - Test desktop width with fixed sidebar.
    - Test mobile/narrow width with the sidebar drawer.
    - Verify the chat input remains usable and text does not overflow.

11. Verify loading/error states.
    - Observe `Loading conversations...`, `Loading conversation...`, and generation loading text.
    - Stop the backend and send a message to verify a visible error appears.

12. Verify unsafe HTML is not executed/rendered unsafely.
    - Use or create an artifact containing unsafe HTML through a controlled backend test path.
    - Verify scripts or unsafe event handlers do not execute in the browser.

13. Verify conversation persists after refresh.
    - Refresh the browser.
    - Verify conversations reload from the backend and messages retain their sources.
