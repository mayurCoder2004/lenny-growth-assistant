# Lenny Growth Assistant - Design Document

## 1. Design Principles

- Clarity: the interface centers on the active conversation and the generated answer.
- Evidence visibility: assistant messages show a `Sources` section when source metadata is returned.
- Readable long-form content: artifacts render in a dedicated document-style viewer.
- Low cognitive load: the UI uses one primary chat surface, a session sidebar, and a simple agent selector.
- Trustworthy AI interaction: source links remain attached to assistant responses.
- Clear loading/error states: conversations, messages, and generation expose visible status text.

## 2. Information Architecture

The frontend lives under `frontend/src/` and is organized around:

- `App.jsx`: application state, session/message/artifact orchestration, layout composition.
- `components/layout/TopBar.jsx`: product title, mobile sidebar trigger, new chat control.
- `components/layout/Sidebar.jsx`: conversation drawer/sidebar, loading and empty states.
- `components/chat/ConversationList.jsx`: conversation rows and delete controls.
- `components/chat/ChatMessage.jsx`: user/assistant message rendering and source links.
- `components/chat/ChatInput.jsx`: agent selector, text input, send button.
- `components/artifacts/ArtifactHeader.jsx`: artifact title/status header.
- `components/artifacts/ArtifactViewer.jsx`: sanitized HTML artifact rendering.
- `components/ui/ConfirmDialog.jsx` and `Toast.jsx`: delete confirmation and notifications.
- `api/*.js`: hard-coded local API client helpers.

## 3. Main Chat Experience

The application displays a dark workspace with a fixed top bar, a desktop sidebar, a mobile drawer sidebar, a scrollable chat area, and a fixed input area. Conversations load on startup through `getUserSessions(user.id)`. Selecting a conversation loads messages through `getSessionMessages(activeSessionId)`.

Messages are rendered by `ChatMessage.jsx`. User messages use plain pre-wrapped text. Assistant messages use `ReactMarkdown` inside `.markdown-body`, followed by a `Sources` block when `sources.length > 0`.

`ChatInput.jsx` provides a select control with `Chat` and `Ship30 Essay`, a text input, and a submit button. Empty messages are blocked. While loading, controls are disabled and the button changes to `Generating...`.

## 4. Ship30 Experience

The UI-facing Ship30 essay path is selected with the `Ship30 Essay` option in `ChatInput.jsx`, which sends `agent: "artifact"` to the chat API. The backend generates a grounded essay and persists it as an artifact.

The backend also includes a `Ship30Agent` for structured 30-day plans. It returns a rendered Markdown plan and a `Ship30Plan` object in the chat response when called with `agent: "ship30"`, but this option is not exposed in the current frontend selector.

## 5. Artifact Viewer

When a chat response includes `artifact_id`, `App.jsx` calls `getArtifact()` and stores the returned artifact in state with `status: "Saved"`. `ArtifactHeader.jsx` displays the artifact label, title, type, timestamp field, and visual Copy/Export buttons. The timestamp expression currently reads `artifact.createdAt`, while the API returns `created_at`, so the timestamp may not render. `ArtifactViewer.jsx` renders the artifact content with `dangerouslySetInnerHTML`; the backend sanitizes artifact HTML before persistence.

The Copy and Export buttons are currently visual controls only. No handlers are wired.

## 6. Sources UX

Sources are attached to assistant responses, not displayed as a separate global panel. `ChatMessage.jsx` renders a `Sources` heading and one link per source. The link text prefers `source.title`, then `source.guest`, then `source.url`.

Backend source metadata can include `evidence_id`, `source_id`, `guest`, `title`, `url`, `distance`, and `chunk_index` depending on the path. The artifact flow preserves full `Evidence` objects through `Ship30Essay`, then `ArtifactAgent` returns `evidence_id`, `source_id`, `guest`, `title`, and `url`. `ChatService` persists those sources on the assistant `Message.sources` JSONB column. The immediate `ChatResponse` is shaped by `ChatSource`, which currently omits `source_id`; reloaded messages use raw persisted source dictionaries.

## 7. Loading States

Implemented loading states include:

- `Loading conversations...` in `Sidebar.jsx`.
- `Loading conversation...` in `App.jsx` while messages load.
- `Generating artifact...` in `App.jsx` while any chat request is in flight.
- `Generating...` send button text in `ChatInput.jsx`.

The generation loading text is generic to the current implementation and appears for chat requests as well as artifact requests.

## 8. Error States

`App.jsx` stores errors in a single `error` state and renders them in a red-toned bordered block. API helpers throw errors that include HTTP status and response text for sessions/chat. Delete failures also show an error toast through `Toast.jsx`.

Backend endpoints return 404 for missing users, sessions, and artifacts where implemented, and 500 for chat/artifact service failures.

## 9. Empty States

Implemented empty states include:

- `No chats yet.` in the sidebar when no conversations exist.
- `Start with a growth question.` in the main area when an active session has no messages and no artifact is loading.
- `Your generated artifact will appear here when it is ready.` under the initial empty chat prompt.

## 10. Responsive Design

The layout uses Tailwind responsive classes. On large screens, the sidebar is a fixed left column in a `lg:grid-cols-[286px_minmax(0,1fr)]` layout. On smaller screens, the sidebar becomes an off-canvas drawer controlled from `TopBar.jsx`. The chat area and input use constrained max widths and `min-w-0` to avoid overflow.

## 11. Accessibility

Existing accessibility considerations include semantic buttons, `aria-label` values for sidebar open/close and conversation deletion, focus rings on interactive controls, keyboard Escape handling for the mobile sidebar, and `rel="noopener noreferrer"` for external source links.

Formal accessibility compliance has not been implemented or tested.

## 12. Visual Design

The UI uses a dark color system centered on `#0b0f17`, `#0d121b`, `#10151e`, and `#111722`, with borders such as `#202938` and text colors such as `#e8edf5`, `#b9c2d0`, and `#8c97a9`. Source links use `#8fa9ff`.

Typography uses Inter with system fallbacks. The interface uses compact rounded cards, subtle borders, and restrained shadows. Markdown and artifact content have separate CSS blocks: `.markdown-body` for assistant messages and `.artifact-document` for long-form artifact presentation.

## 13. Design Decisions

- Keep chat and artifact output in one workspace so the user does not switch contexts.
- Attach sources directly under assistant messages so evidence is close to the claim it supports.
- Use a simple agent selector instead of separate pages for chat and Ship30 essay generation.
- Render artifacts as document content after generation, while keeping the original assistant response in the message stream.
- Use a fixed demo user for evaluator simplicity; this is not a production account model.
