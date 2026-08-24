function TopBar({ onNewChat, onOpenSidebar }) {
  return (
    <header className="box-border flex h-16 w-full min-w-0 items-center justify-between gap-3 border-b border-[#1c2330] bg-[#0b0f17]/95 px-3 backdrop-blur sm:h-[68px] sm:px-5 lg:px-7">
      <div className="flex min-w-0 flex-1 items-center gap-2.5 sm:gap-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-[#202938] bg-[#111722] text-[#dce2eb] transition duration-150 hover:border-[#27303e] hover:bg-[#171e29] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15 lg:hidden"
          aria-label="Open conversations"
        >
          <span
            className="flex w-4 flex-col gap-1"
            aria-hidden="true"
          >
            <span className="h-px rounded-full bg-current" />
            <span className="h-px rounded-full bg-current" />
            <span className="h-px rounded-full bg-current" />
          </span>
        </button>

        <div className="hidden h-9 w-9 shrink-0 place-items-center rounded-lg border border-[#dfe5ef]/10 bg-[#e8edf5] text-sm font-extrabold text-[#0b0f17] shadow-[0_8px_24px_rgba(0,0,0,0.22)] min-[430px]:grid lg:grid">
          L
        </div>

        <div className="min-w-0 flex-1">
          <h1 className="truncate text-[13px] font-semibold leading-5 text-[#f0f3f8] min-[390px]:text-sm sm:text-[15px]">
            Lenny Growth Assistant
          </h1>

          <span className="hidden truncate text-xs leading-4 text-[#7e899b] sm:block">
            Product growth workspace
          </span>
        </div>
      </div>

      <button
        type="button"
        onClick={onNewChat}
        className="shrink-0 rounded-lg border border-[#f0f3f8]/10 bg-[#e8edf5] px-2.5 py-2 text-xs font-semibold text-[#0b0f17] shadow-[0_8px_24px_rgba(0,0,0,0.22)] transition duration-150 hover:bg-white active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/25 min-[390px]:px-3 sm:px-3.5"
      >
        <span className="sm:hidden">New</span>
        <span className="hidden sm:inline">+ New Chat</span>
      </button>
    </header>
  );
}

export default TopBar;
