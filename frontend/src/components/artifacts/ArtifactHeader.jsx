function ArtifactHeader({ artifact }) {
  return (
    <div className="mb-6 flex flex-col gap-4 border-t border-[#1c2330]/70 pt-8 sm:mb-7 sm:flex-row sm:items-start sm:justify-between sm:gap-8">
      <div className="min-w-0">
        <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[#7e899b]">
          Artifact
        </span>

        <h2 className="mt-2 max-w-[720px] text-[1.65rem] font-semibold leading-tight text-[#f0f3f8] sm:text-[2rem]">
          {artifact.title}
        </h2>

        <p className="mt-2 text-xs leading-5 text-[#8c97a9]">
          {artifact.type} - {artifact.createdAt}
        </p>
      </div>

      <div className="flex shrink-0 gap-2 sm:pt-2">
        <button
          type="button"
          className="rounded-lg border border-[#27303e] bg-[#111722] px-3.5 py-2 text-xs font-semibold text-[#cbd4e2] transition duration-150 hover:border-[#3a4658] hover:bg-[#171e29] active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/15"
        >
          Copy
        </button>

        <button
          type="button"
          className="rounded-lg border border-[#f0f3f8]/10 bg-[#e8edf5] px-3.5 py-2 text-xs font-semibold text-[#0b0f17] transition duration-150 hover:bg-white active:translate-y-px focus:outline-none focus:ring-2 focus:ring-[#edf1f7]/25"
        >
          Export
        </button>
      </div>
    </div>
  );
}

export default ArtifactHeader;
