function ArtifactViewer({ artifact }) {
  return (
    <article className="overflow-hidden rounded-xl border border-[#202938] bg-[#10151e] shadow-[0_24px_70px_rgba(0,0,0,0.22),0_1px_0_rgba(255,255,255,0.03)_inset]">
      <div className="flex items-center justify-between gap-4 border-b border-[#202938] bg-[#111722]/55 px-4 py-3.5 sm:px-5">
        <span className="rounded-md border border-[#27303e] bg-[#181f2b] px-2.5 py-1 text-[11px] font-semibold text-[#c2ccda]">
          Ship30 Essay
        </span>

        <span className="text-[11px] font-medium text-[#768195]">
          {artifact.status}
        </span>
      </div>

      <div className="mx-auto max-w-[820px] px-5 py-8 pb-12 sm:px-9 sm:py-10 sm:pb-14 lg:px-14 lg:py-12 lg:pb-16">
        <div
          className="artifact-document max-w-none"
          dangerouslySetInnerHTML={{
            __html: artifact.content,
          }}
        />
      </div>
    </article>
  );
}

export default ArtifactViewer;
