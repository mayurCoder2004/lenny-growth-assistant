import ReactMarkdown from "react-markdown";

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
        <div className="prose prose-invert max-w-none prose-headings:text-[#edf1f7] prose-h1:mb-6 prose-h1:text-3xl prose-h1:font-semibold prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-2xl prose-h2:font-semibold prose-h3:mt-8 prose-h3:mb-3 prose-h3:text-lg prose-h3:font-semibold prose-p:text-[15px] prose-p:leading-[1.8] prose-p:text-[#b9c2d0] prose-strong:text-[#edf1f7] prose-li:text-[#b9c2d0] prose-code:text-[#dce2eb]">
          <ReactMarkdown>
            {artifact.content}
          </ReactMarkdown>
        </div>
      </div>
    </article>
  );
}

export default ArtifactViewer;
