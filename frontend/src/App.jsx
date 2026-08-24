import { useEffect, useState } from "react";

import TopBar from "./components/layout/TopBar";
import Sidebar from "./components/layout/Sidebar";
import ChatInput from "./components/chat/ChatInput";
import ChatMessage from "./components/chat/ChatMessage";
import ArtifactHeader from "./components/artifacts/ArtifactHeader";
import ArtifactViewer from "./components/artifacts/ArtifactViewer";

import { sendChatMessage } from "./api/chat";
import { getArtifact } from "./api/artifacts";
import {
  createSession,
  getUserSessions,
  getSessionMessages,
} from "./api/sessions";

import { user } from "./data/mockData";

function App() {
  const [conversations, setConversations] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [artifact, setArtifact] = useState(null);

  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [creatingSession, setCreatingSession] = useState(false);
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadSessions() {
      try {
        setSessionsLoading(true);
        setError("");

        const data = await getUserSessions(user.id);

        const formattedSessions = data.map((session) => ({
          id: session.id,
          title: session.title,
          time: new Date(
            session.updated_at
          ).toLocaleDateString(),
        }));

        setConversations(formattedSessions);

        if (formattedSessions.length > 0) {
          setActiveSessionId(
            formattedSessions[0].id
          );
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load conversations."
        );
      } finally {
        setSessionsLoading(false);
      }
    }

    loadSessions();
  }, []);

  useEffect(() => {
    if (!activeSessionId) {
      setMessages([]);
      setArtifact(null);
      return;
    }

    async function loadMessages() {
      try {
        setMessagesLoading(true);
        setError("");
        setArtifact(null);

        const data = await getSessionMessages(
          activeSessionId
        );

        setMessages(
          data.map((message) => ({
            role: message.role,
            content: message.content,
          }))
        );
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Failed to load messages."
        );

        setMessages([]);
      } finally {
        setMessagesLoading(false);
      }
    }

    loadMessages();
  }, [activeSessionId]);

  async function handleNewConversation() {
    if (creatingSession) {
      return;
    }

    try {
      setCreatingSession(true);
      setError("");

      const newSession = await createSession({
        userId: user.id,
        title: "New Chat",
      });

      const formattedSession = {
        id: newSession.id,
        title: newSession.title,
        time: new Date(
          newSession.updated_at
        ).toLocaleDateString(),
      };

      setConversations((current) => [
        formattedSession,
        ...current,
      ]);

      setActiveSessionId(newSession.id);
      setMessages([]);
      setArtifact(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create conversation."
      );
    } finally {
      setCreatingSession(false);
    }
  }

  function handleSelectConversation(sessionId) {
    if (sessionId === activeSessionId) {
      return;
    }

    setArtifact(null);
    setMessages([]);
    setActiveSessionId(sessionId);
  }

  async function handleSend(message) {
    if (!activeSessionId) {
      setError("Please select a conversation first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      setMessages((current) => [
        ...current,
        {
          role: "user",
          content: message,
        },
      ]);

      const response = await sendChatMessage({
        sessionId: activeSessionId,
        message,
        agent: "artifact",
      });

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
        },
      ]);

      if (response.artifact_id) {
        const generatedArtifact =
          await getArtifact(
            response.artifact_id
          );

        setArtifact({
          ...generatedArtifact,
          status: "Saved",
        });
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0b0f17] text-[#e8edf5]">
      <TopBar />

      <main className="grid min-h-[calc(100vh-72px)] grid-cols-[260px_1fr]">
        <Sidebar
          conversations={conversations}
          activeConversationId={activeSessionId}
          onSelectConversation={
            handleSelectConversation
          }
          onNewConversation={
            handleNewConversation
          }
          loading={
            sessionsLoading ||
            creatingSession
          }
        />

        <section className="flex min-h-[calc(100vh-72px)] flex-col">
          <div className="flex-1 overflow-y-auto px-8 py-8">
            <div className="mx-auto max-w-[1000px]">
              <div className="mb-8">
                <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#7e899b]">
                  Growth Assistant
                </span>

                <h2 className="mt-2 text-2xl font-semibold text-[#f0f3f8]">
                  What are you working on?
                </h2>

                <p className="mt-2 text-sm text-[#768195]">
                  Ask a product growth question or
                  generate a Ship30 essay.
                </p>
              </div>

              {messagesLoading && (
                <div className="mb-5 rounded-lg border border-[#202938] bg-[#10151e] px-4 py-3 text-sm text-[#768195]">
                  Loading conversation...
                </div>
              )}

              <div className="flex flex-col gap-4">
                {messages.map(
                  (message, index) => (
                    <ChatMessage
                      key={`${message.role}-${index}`}
                      role={message.role}
                      content={message.content}
                    />
                  )
                )}
              </div>

              {loading && (
                <div className="mt-4 flex justify-start">
                  <div className="rounded-xl bg-[#10151e] px-4 py-3 text-sm text-[#768195]">
                    Generating artifact...
                  </div>
                </div>
              )}

              {error && (
                <div className="mt-5 rounded-lg border border-[#3a2930] bg-[#151018] px-4 py-3 text-sm text-[#c8aeb8]">
                  {error}
                </div>
              )}

              {artifact && (
                <div className="mt-10">
                  <ArtifactHeader
                    artifact={artifact}
                  />

                  <ArtifactViewer
                    artifact={artifact}
                  />
                </div>
              )}

              {!artifact &&
                !loading &&
                !messagesLoading &&
                messages.length === 0 &&
                activeSessionId && (
                  <div className="mt-10 rounded-xl border border-[#202938] bg-[#10151e] p-6 text-sm text-[#768195]">
                    Start a conversation to generate
                    your first artifact.
                  </div>
                )}
            </div>
          </div>

          <ChatInput
            onSend={handleSend}
            loading={
              loading ||
              sessionsLoading ||
              messagesLoading ||
              creatingSession
            }
          />
        </section>
      </main>
    </div>
  );
}

export default App;
