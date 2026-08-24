function ArtifactHeader({ artifact }) {
  return (
    <div className="mb-7 flex items-start justify-between gap-8">
      <div>
        <span className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#7e899b]">
          Artifact
        </span>

        <h2 className="mt-1.5 max-w-[650px] text-[28px] font-semibold leading-tight tracking-[-0.02em] text-[#f0f3f8]">
          {artifact.title}
        </h2>

        <p className="mt-1.5 text-xs text-[#768195]">
          {artifact.type} Â· {artifact.createdAt}
        </p>
      </div>

      <div className="flex gap-2 pt-2">
        <button
          type="button"
          className="rounded-lg border border-[#27303e] bg-[#111722] px-3.5 py-2 text-xs font-semibold text-[#bfc8d6] transition hover:bg-[#171e29]"
        >
          Copy
        </button>

        <button
          type="button"
          className="rounded-lg bg-[#e8edf5] px-3.5 py-2 text-xs font-semibold text-[#0b0f17] transition hover:bg-white"
        >
          Export
        </button>
      </div>
    </div>
  );
}

export default ArtifactHeader;
