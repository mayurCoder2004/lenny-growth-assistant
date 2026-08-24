function TopBar({ onNewChat }) {
  return (
    <header className="flex h-[72px] items-center justify-between border-b border-[#1c2330] bg-[#0b0f17] px-7">
      <div className="flex items-center gap-3">
        <div className="grid h-9 w-9 place-items-center rounded-[10px] bg-[#e8edf5] font-extrabold text-[#0b0f17]">
          L
        </div>

        <div>
          <h1 className="text-[15px] font-semibold">
            Lenny Growth Assistant
          </h1>

          <span className="text-xs text-[#7e899b]">
            Product growth workspace
          </span>
        </div>
      </div>

      <button
        type="button"
        onClick={onNewChat}
        className="rounded-lg bg-[#e8edf5] px-3.5 py-2 text-xs font-semibold text-[#0b0f17] transition hover:bg-white"
      >
        + New Chat
      </button>
    </header>
  );
}

export default TopBar;
