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
          "max-w-[min(780px,100%)] rounded-xl px-4 py-3 text-sm leading-7 shadow-[0_10px_30px_rgba(0,0,0,0.14)] sm:px-5 sm:py-4",
          isUser
            ? "border border-[#27303e] bg-[#171e29] text-[#dce2eb]"
            : "border border-[#202938] bg-[#10151e] text-[#b9c2d0]",
        ].join(" ")}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-7">
            {content}
          </p>
        ) : (
          <div className="markdown-body">
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
