"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Raw HTML in markdown is NOT rendered (react-markdown default) — safe for LLM output.
export function Markdown({ children }: { children: string }) {
  return (
    <div className="prose-hd">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}
