import { fluidSize } from "@/lib/utils";

export default function AirdropLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="min-h-screen h-screen"
      style={{ padding: fluidSize(16, 24) }}
    >
      {children}
    </div>
  );
}
