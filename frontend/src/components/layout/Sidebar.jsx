import { useEffect } from "react";

import ConversationList from "../chat/ConversationList";

function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  loading,
  isOpen,
  onClose,
}) {
  const drawerMode = typeof isOpen === "boolean";

  useEffect(() => {
    if (!drawerMode || !isOpen) {
      return undefined;
    }

    function handleKeyDown(event) {
      if (event.key === "Escape") {
        onClose?.();
      }
    }

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [drawerMode, isOpen, onClose]);

  const sidebarContent = (
    <>
      <div className="mb-3.5 flex items-center justify-between gap-2 px-1.5 sm:px-2">
        <span className="truncate text-[11px] font-semibold uppercase tracking-[0.14em] text-[#8c97a9]">
          Conversations
        </span>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onNewConversation}
            className="grid h-7 w-7 shrink-0 place-items-center rounded-md border border-[#202938] bg-[#111722] text-sm font-medium text-[#dce2eb] transition duration-150 hover:border-[#27303e] hover:bg-[#171e29] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15"
            aria-label="New conversation"
          >
            +
          </button>

          {drawerMode && (
            <button
              type="button"
              onClick={onClose}
              className="grid h-7 w-7 shrink-0 place-items-center rounded-md border border-[#202938] bg-[#111722] text-sm font-medium text-[#aeb8c8] transition duration-150 hover:border-[#27303e] hover:bg-[#171e29] hover:text-[#edf1f7] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15 lg:hidden"
              aria-label="Close conversations"
            >
              x
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="rounded-lg border border-[#202938]/70 bg-[#10151e]/60 px-2.5 py-3 text-xs leading-5 text-[#768195]">
          Loading conversations...
        </div>
      ) : conversations.length === 0 ? (
        <div className="rounded-lg border border-dashed border-[#27303e] px-2.5 py-4 text-xs leading-5 text-[#768195]">
          No chats yet.
        </div>
      ) : (
        <ConversationList
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelect={onSelectConversation}
          onDelete={onDeleteConversation}
        />
      )}
    </>
  );

  if (drawerMode) {
    return (
      <>
        <button
          type="button"
          className={[
            "fixed inset-x-0 top-16 bottom-0 z-40 bg-[#05070b]/65 backdrop-blur-sm transition-opacity duration-200 sm:top-[68px] lg:hidden",
            isOpen
              ? "pointer-events-auto opacity-100"
              : "pointer-events-none opacity-0",
          ].join(" ")}
          onClick={onClose}
          aria-label="Close conversations"
        />

        <aside
          className={[
            "fixed top-16 bottom-0 left-0 z-50 flex w-[min(320px,calc(100vw-48px))] max-w-full flex-col overflow-y-auto border-r border-[#27303e] bg-[#0d121b] p-3.5 shadow-[24px_0_80px_rgba(0,0,0,0.42)] transition-transform duration-200 ease-out sm:top-[68px] lg:hidden",
            isOpen ? "translate-x-0" : "-translate-x-full",
          ].join(" ")}
          aria-label="Conversations"
        >
          {sidebarContent}
        </aside>
      </>
    );
  }

  return (
    <aside className="h-full min-h-0 overflow-y-auto border-r border-[#1c2330] bg-[#0d121b] p-3.5">
      {sidebarContent}
    </aside>
  );
}

export default Sidebar;
