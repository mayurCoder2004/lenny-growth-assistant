import ReactMarkdown from "react-markdown";

function ChatMessage({
  role,
  content,
  sources = [],
}) {
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
          <>
            <div className="markdown-body">
              <ReactMarkdown>
                {content}
              </ReactMarkdown>
            </div>

            {sources.length > 0 && (
              <div className="mt-5 border-t border-[#202938] pt-4">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#7e899b]">
                  Sources
                </p>

                <div className="space-y-2">
                  {sources.map((source, index) => (
                    <a
                      key={
                        source.evidence_id ||
                        `${source.url}-${index}`
                      }
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-sm text-[#8fa9ff] hover:underline"
                    >
                      {source.title ||
                        source.guest ||
                        source.url}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
