function ConversationList({
  conversations,
  activeConversationId,
  onSelect,
}) {
  return (
    <div className="flex flex-col gap-1">
      {conversations.map((conversation) => {
        const active =
          conversation.id === activeConversationId;

        return (
          <button
            key={conversation.id}
            type="button"
            onClick={() => onSelect(conversation.id)}
            className={[
              "flex w-full flex-col items-start gap-1.5 rounded-lg px-2.5 py-2.5 text-left transition",
              active
                ? "bg-[#171e29]"
                : "hover:bg-[#171e29]",
            ].join(" ")}
          >
            <span className="text-[13px] text-[#b9c2d0]">
              {conversation.title}
            </span>

            <span className="text-[11px] text-[#687386]">
              {conversation.time}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export default ConversationList;
