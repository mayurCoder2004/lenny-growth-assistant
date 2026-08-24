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
  getUserSessions,
  getSessionMessages,
  createSession,
  deleteSession,
} from "./api/sessions";

import { user } from "./data/mockData";


function App() {
  const [conversations, setConversations] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);

  const [messages, setMessages] = useState([]);
  const [artifact, setArtifact] = useState(null);

  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
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
          setActiveSessionId(formattedSessions[0].id);
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
      return;
    }

    async function loadMessages() {
      try {
        setMessagesLoading(true);
        setError("");

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
    try {
      setError("");

      const newSession = await createSession({
        userId: user.id,
        title: "New Chat",
      });

      const conversation = {
        id: newSession.id,
        title: newSession.title,
        time: new Date(
          newSession.updated_at
        ).toLocaleDateString(),
      };

      setConversations((current) => [
        conversation,
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
    }
  }


  async function handleSelectConversation(sessionId) {
    if (sessionId === activeSessionId) {
      return;
    }

    setArtifact(null);
    setActiveSessionId(sessionId);
  }


  async function handleDeleteConversation(sessionId) {
    const conversation = conversations.find(
      (item) => item.id === sessionId
    );

    if (!conversation) {
      return;
    }

    const confirmed = window.confirm(
      `Delete "${conversation.title}"? This cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteSession(sessionId);

      const remaining = conversations.filter(
        (item) => item.id !== sessionId
      );

      setConversations(remaining);

      if (sessionId === activeSessionId) {
        const nextConversation = remaining[0];

        if (nextConversation) {
          setActiveSessionId(nextConversation.id);
          setMessages([]);
          setArtifact(null);
        } else {
          setActiveSessionId(null);
          setMessages([]);
          setArtifact(null);
        }
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete conversation."
      );
    }
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

      const updatedSessions =
        await getUserSessions(user.id);

      const formattedSessions =
        updatedSessions.map((session) => ({
          id: session.id,
          title: session.title,
          time: new Date(
            session.updated_at
          ).toLocaleDateString(),
        }));

      setConversations(formattedSessions);
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
    <div className="flex h-screen flex-col overflow-hidden bg-[#0b0f17] text-[#e8edf5]">

      <div className="shrink-0">
        <TopBar
          onNewChat={handleNewConversation}
        />
      </div>


      <main className="grid min-h-0 flex-1 grid-cols-[260px_1fr] overflow-hidden">

        <Sidebar
          conversations={conversations}
          activeConversationId={activeSessionId}
          onSelectConversation={
            handleSelectConversation
          }
          onNewConversation={
            handleNewConversation
          }
          onDeleteConversation={
            handleDeleteConversation
          }
          loading={sessionsLoading}
        />


        <section className="flex min-h-0 flex-col overflow-hidden">

          <div className="min-h-0 flex-1 overflow-y-auto px-8 py-8">

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


          <div className="shrink-0">
            <ChatInput
              onSend={handleSend}
              loading={
                loading ||
                sessionsLoading ||
                messagesLoading
              }
            />
          </div>

        </section>
      </main>
    </div>
  );
}


export default App;
