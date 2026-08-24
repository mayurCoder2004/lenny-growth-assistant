function ConversationList({
  conversations,
  activeConversationId,
  onSelect,
  onDelete,
}) {
  return (
    <div className="flex flex-col gap-1">
      {conversations.map((conversation) => {
        const active =
          conversation.id === activeConversationId;

        return (
          <div
            key={conversation.id}
            className={[
              "group flex items-center gap-1 rounded-lg transition",
              active
                ? "bg-[#171e29]"
                : "hover:bg-[#171e29]",
            ].join(" ")}
          >
            <button
              type="button"
              onClick={() => onSelect(conversation.id)}
              className="min-w-0 flex-1 px-2.5 py-2.5 text-left"
            >
              <span className="block truncate text-[13px] text-[#b9c2d0]">
                {conversation.title}
              </span>

              <span className="mt-1 block text-[11px] text-[#687386]">
                {conversation.time}
              </span>
            </button>

            <button
              type="button"
              onClick={() => onDelete(conversation.id)}
              className="mr-1 hidden h-7 w-7 shrink-0 place-items-center rounded-md text-[#687386] transition hover:bg-[#202938] hover:text-[#c8aeb8] group-hover:grid"
              aria-label={`Delete ${conversation.title}`}
              title="Delete conversation"
            >
              X
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default ConversationList;
