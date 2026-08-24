function ChatMessage({ role, content }) {
  const isUser = role === "user";

  return (
    <div
      className={[
        "flex",
        isUser ? "justify-end" : "justify-start",
      ].join(" ")}
    >
      <div
        className={[
          "max-w-[760px] rounded-xl px-4 py-3 text-sm leading-7",
          isUser
            ? "bg-[#171e29] text-[#dce2eb]"
            : "bg-[#10151e] text-[#b9c2d0]",
        ].join(" ")}
      >
        {content}
      </div>
    </div>
  );
}

export default ChatMessage;
