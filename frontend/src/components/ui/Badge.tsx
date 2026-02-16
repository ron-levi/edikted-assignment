const STAGE_COLORS: Record<string, string> = {
  CONCEPT: "bg-gray-100 text-gray-700",
  DESIGN: "bg-blue-100 text-blue-700",
  DEVELOPMENT: "bg-yellow-100 text-yellow-700",
  SAMPLING: "bg-purple-100 text-purple-700",
  PRODUCTION: "bg-green-100 text-green-700",
  OFFERED: "bg-gray-100 text-gray-700",
  APPROVED: "bg-green-100 text-green-700",
  REJECTED: "bg-red-100 text-red-700",
  IN_PRODUCTION: "bg-emerald-100 text-emerald-700",
  IN_STORE: "bg-teal-100 text-teal-700",
  PENDING: "bg-yellow-100 text-yellow-700",
  RECEIVED: "bg-blue-100 text-blue-700",
};

export function Badge({ label, className = "" }: { label: string; className?: string }) {
  const colors = STAGE_COLORS[label] || "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors} ${className}`}>
      {label.replace(/_/g, " ")}
    </span>
  );
}
