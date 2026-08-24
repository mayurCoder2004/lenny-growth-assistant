import ReactMarkdown from "react-markdown";

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
        {isUser ? (
          <p className="whitespace-pre-wrap">
            {content}
          </p>
        ) : (
          <div className="prose prose-invert max-w-none prose-headings:text-[#edf1f7] prose-p:text-[#b9c2d0] prose-strong:text-[#edf1f7] prose-li:text-[#b9c2d0] prose-code:text-[#dce2eb]">
            <ReactMarkdown>
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
