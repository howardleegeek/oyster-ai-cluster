export default function CheckEligibilityLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="w-full min-h-full flex items-center justify-center">
      {children}
    </div>
  );
}
