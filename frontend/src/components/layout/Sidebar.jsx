import ConversationList from "../chat/ConversationList";

function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  loading,
}) {
  return (
    <aside className="min-h-0 overflow-y-auto border-r border-[#1c2330] bg-[#0d121b] p-3.5">

      <div className="mb-3.5 flex items-center justify-between px-2">
        <span className="text-[11px] font-semibold uppercase tracking-[0.08em] text-[#8c97a9]">
          Conversations
        </span>

        <button
          type="button"
          onClick={onNewConversation}
          className="grid h-[26px] w-[26px] place-items-center rounded-md bg-[#171e29] text-[#aeb8c8] transition hover:bg-[#202938]"
          aria-label="New conversation"
        >
          +
        </button>
      </div>

      {loading ? (
        <div className="px-2 py-3 text-xs text-[#687386]">
          Loading conversations...
        </div>
      ) : conversations.length === 0 ? (
        <div className="px-2 py-3 text-xs text-[#687386]">
          No conversations yet.
        </div>
      ) : (
        <ConversationList
          conversations={conversations}
          activeConversationId={activeConversationId}
          onSelect={onSelectConversation}
          onDelete={onDeleteConversation}
        />
      )}

    </aside>
  );
}

export default Sidebar;
