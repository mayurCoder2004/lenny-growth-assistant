import { useState } from "react";

function ChatInput({
  onSend,
  loading,
  agent,
  onAgentChange,
}) {
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
      className="box-border w-full min-w-0 shrink-0 border-t border-[#202938] bg-[#0d121b]/95 px-3 py-3 backdrop-blur sm:px-5 sm:py-4"
    >
      <div className="mx-auto flex w-full max-w-[820px] flex-col gap-2 rounded-xl border border-[#27303e] bg-[#111722] p-1.5 shadow-[0_16px_46px_rgba(0,0,0,0.24),0_1px_0_rgba(255,255,255,0.03)_inset] transition focus-within:border-[#465267] focus-within:ring-2 focus-within:ring-[#edf1f7]/10">

        <div className="flex items-center gap-2">
          <select
            value={agent}
            onChange={(event) =>
              onAgentChange(event.target.value)
            }
            disabled={loading}
            className="shrink-0 rounded-lg border border-[#27303e] bg-[#171e29] px-2.5 py-2 text-xs font-medium text-[#b9c2d0] outline-none focus:border-[#465267] disabled:opacity-50"
          >
            <option value="chat">
              Chat
            </option>

            <option value="artifact">
              Ship30 Essay
            </option>
          </select>

          <input
            type="text"
            value={message}
            onChange={(event) =>
              setMessage(event.target.value)
            }
            placeholder={
              agent === "artifact"
                ? "Describe the Ship30 essay you want..."
                : "Ask about product growth..."
            }
            disabled={loading}
            className="min-w-0 flex-1 rounded-lg border-0 bg-transparent px-3 py-2.5 text-sm leading-6 text-[#e8edf5] outline-none placeholder:text-[#687386] disabled:opacity-50 sm:px-3.5"
          />

          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="shrink-0 rounded-lg border border-[#f0f3f8]/10 bg-[#e8edf5] px-3.5 py-2.5 text-xs font-semibold text-[#0b0f17] transition duration-150 hover:bg-white active:translate-y-px disabled:cursor-not-allowed disabled:opacity-40 sm:min-w-[78px] sm:px-4"
          >
            {loading ? "Generating..." : "Send"}
          </button>
        </div>

      </div>

      <div className="mx-auto mt-2 hidden max-w-[820px] px-1 text-[11px] text-[#687386] sm:block">
        Press Enter to send.
      </div>
    </form>
  );
}

export default ChatInput;
