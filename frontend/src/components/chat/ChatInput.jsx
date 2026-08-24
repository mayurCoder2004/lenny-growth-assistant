import { useState } from "react";

function ChatInput({ onSend, loading }) {
  const [message, setMessage] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    await onSend(trimmedMessage);
    setMessage("");
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="shrink-0 border-t border-[#202938] bg-[#0d121b] p-4"
    >
      <div className="mx-auto flex max-w-[760px] gap-2">

        <input
          type="text"
          value={message}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          placeholder="Ask about product growth..."
          disabled={loading}
          className="min-w-0 flex-1 rounded-lg border border-[#27303e] bg-[#111722] px-3.5 py-3 text-sm text-[#e8edf5] outline-none placeholder:text-[#687386] focus:border-[#465267] disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="rounded-lg bg-[#e8edf5] px-4 py-3 text-xs font-semibold text-[#0b0f17] transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Generating..." : "Send"}
        </button>

      </div>
    </form>
  );
}

export default ChatInput;
