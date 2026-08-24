import { useEffect, useState } from "react";

import TopBar from "./components/layout/TopBar";
import Sidebar from "./components/layout/Sidebar";
import ChatInput from "./components/chat/ChatInput";
import ChatMessage from "./components/chat/ChatMessage";
import ArtifactHeader from "./components/artifacts/ArtifactHeader";
import ArtifactViewer from "./components/artifacts/ArtifactViewer";
import ConfirmDialog from "./components/ui/ConfirmDialog";
import ToastContainer from "./components/ui/Toast";

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
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [toasts, setToasts] = useState([]);


  function showToast(message, type = "success") {
    const id = window.crypto?.randomUUID
      ? window.crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`;

    setToasts((current) => [
      ...current,
      {
        id,
        message,
        type,
      },
    ]);
  }


  function dismissToast(toastId) {
    setToasts((current) =>
      current.filter((toast) => toast.id !== toastId)
    );
  }


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
      setSidebarOpen(false);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create conversation."
      );
    }
  }


  async function handleSelectConversation(sessionId) {
    setSidebarOpen(false);

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

    setDeleteTarget(conversation);
  }


  async function handleConfirmDeleteConversation() {
    if (!deleteTarget) {
      return;
    }

    const sessionId = deleteTarget.id;

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

      setDeleteTarget(null);
      setSidebarOpen(false);
      showToast("Conversation deleted", "success");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete conversation."
      );

      showToast("Failed to delete conversation.", "error");
      setDeleteTarget(null);
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
    <div className="box-border flex h-screen w-full min-w-0 flex-col overflow-hidden bg-[#0b0f17] text-[#e8edf5]">

      <div className="shrink-0">
        <TopBar
          onNewChat={handleNewConversation}
          onOpenSidebar={() => setSidebarOpen(true)}
        />
      </div>


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
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />


      <main className="grid min-h-0 w-full min-w-0 flex-1 grid-cols-[minmax(0,1fr)] overflow-hidden lg:grid-cols-[286px_minmax(0,1fr)]">

        <div className="hidden min-h-0 lg:block">
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
        </div>


        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden bg-[#0b0f17]">

          <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-9 lg:py-8">

            <div className="mx-auto w-full max-w-[1040px]">

              <div className="mb-8 border-b border-[#1c2330]/70 pb-7">
                <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[#7e899b]">
                  Growth Assistant
                </span>

                <h2 className="mt-2 max-w-[680px] text-[1.65rem] font-semibold leading-tight text-[#f0f3f8] sm:text-[2rem]">
                  What are you working on?
                </h2>

                <p className="mt-2 max-w-[620px] text-sm leading-6 text-[#8c97a9]">
                  Ask a product growth question or
                  generate a Ship30 essay.
                </p>
              </div>


              {messagesLoading && (
                <div className="mb-5 rounded-lg border border-[#202938] bg-[#10151e]/90 px-4 py-3 text-sm text-[#8c97a9] shadow-[0_1px_0_rgba(255,255,255,0.03)_inset]">
                  Loading conversation...
                </div>
              )}


              <div className="flex flex-col gap-5">
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
                  <div className="rounded-xl border border-[#202938] bg-[#10151e] px-4 py-3 text-sm text-[#8c97a9] shadow-[0_10px_30px_rgba(0,0,0,0.18)]">
                    Generating artifact...
                  </div>
                </div>
              )}


              {error && (
                <div className="mt-5 rounded-lg border border-[#4a2d38] bg-[#151018] px-4 py-3 text-sm leading-6 text-[#e2b8c7]">
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
                  <div className="mt-10 rounded-xl border border-[#202938] bg-[#10151e]/70 p-6 text-sm leading-6 text-[#8c97a9] shadow-[0_1px_0_rgba(255,255,255,0.03)_inset] sm:p-7">
                    <p className="font-medium text-[#dce2eb]">
                      Start with a growth question.
                    </p>

                    <p className="mt-1 text-[#768195]">
                      Your generated artifact will appear
                      here when it is ready.
                    </p>
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

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Delete conversation?"
        description="This conversation and its messages will be permanently deleted. This action cannot be undone."
        cancelLabel="Cancel"
        confirmLabel="Delete conversation"
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleConfirmDeleteConversation}
      />

      <ToastContainer
        toasts={toasts}
        onDismiss={dismissToast}
      />
    </div>
  );
}


export default App;
