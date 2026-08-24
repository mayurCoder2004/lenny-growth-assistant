function ArtifactViewer({ artifact }) {
  return (
    <article className="overflow-hidden rounded-xl border border-[#202938] bg-[#10151e]">
      <div className="flex items-center justify-between border-b border-[#202938] px-[18px] py-3.5">
        <span className="rounded-md bg-[#181f2b] px-2 py-1 text-[11px] font-semibold text-[#aeb8c8]">
          Ship30 Essay
        </span>

        <span className="text-[11px] text-[#6f7c90]">
          {artifact.status}
        </span>
      </div>

      <div className="mx-auto max-w-[760px] px-12 py-[42px] pb-[60px]">
        <p className="mb-6 text-[15px] leading-[1.8] text-[#b9c2d0]">
          {artifact.content}
        </p>

        <h3 className="mb-3 mt-9 text-lg font-semibold text-[#edf1f7]">
          The Core Idea
        </h3>

        <p className="mb-6 text-[15px] leading-[1.8] text-[#b9c2d0]">
          A strong product should help users reach their
          first meaningful outcome quickly. The faster that
          value becomes obvious, the stronger the foundation
          for continued engagement.
        </p>

        <h3 className="mb-3 mt-9 text-lg font-semibold text-[#edf1f7]">
          What to Improve
        </h3>

        <p className="text-[15px] leading-[1.8] text-[#b9c2d0]">
          Focus on the earliest moments of the user journey.
          Remove unnecessary steps, make the value proposition
          obvious, and measure whether users reach the key
          activation event.
        </p>
      </div>
    </article>
  );
}

export default ArtifactViewer;
