export function Logo({ className = "size-8" }: { className?: string }) {
  // D10: auto-generated sample mark (simplified BodyGraph triangle) — replace with real branding.
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect width="32" height="32" rx="9" fill="#3565A8" />
      <path d="M16 6 L24 20 H8 Z" fill="none" stroke="#FBF8F1" strokeWidth="2" strokeLinejoin="round" />
      <rect x="12.5" y="21.5" width="7" height="5" rx="1.2" fill="#C8963E" />
      <circle cx="16" cy="15" r="2.2" fill="#C8963E" />
    </svg>
  );
}
