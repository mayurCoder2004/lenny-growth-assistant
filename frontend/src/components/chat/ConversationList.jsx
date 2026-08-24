function ConversationList({
  conversations,
  activeConversationId,
  onSelect,
  onDelete,
}) {
  return (
    <div className="flex flex-col gap-1.5">
      {conversations.map((conversation) => {
        const active =
          conversation.id === activeConversationId;

        return (
          <div
            key={conversation.id}
            className={[
              "group flex items-center gap-1 rounded-lg border transition duration-150",
              active
                ? "border-[#27303e] bg-[#171e29] shadow-[0_1px_0_rgba(255,255,255,0.03)_inset]"
                : "border-transparent hover:border-[#202938] hover:bg-[#111722]",
            ].join(" ")}
          >
            <button
              type="button"
              onClick={() => onSelect(conversation.id)}
              className="min-w-0 flex-1 rounded-lg px-2 py-2.5 text-left focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15 sm:px-2.5"
            >
              <span
                className={[
                  "block truncate text-[12px] leading-5 sm:text-[13px]",
                  active
                    ? "font-medium text-[#edf1f7]"
                    : "text-[#b9c2d0]",
                ].join(" ")}
              >
                {conversation.title}
              </span>

              <span className="mt-0.5 block truncate text-[10px] leading-4 text-[#687386] sm:text-[11px]">
                {conversation.time}
              </span>
            </button>

            <button
              type="button"
              onClick={() => onDelete(conversation.id)}
              className="mr-1 hidden h-7 w-7 shrink-0 place-items-center rounded-md text-xs text-[#687386] transition duration-150 hover:bg-[#202938] hover:text-[#e2b8c7] focus:outline-none focus:ring-2 focus:ring-[#e2b8c7]/20 group-hover:grid group-focus-within:grid"
              aria-label={`Delete ${conversation.title}`}
              title="Delete conversation"
            >
              x
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default ConversationList;
