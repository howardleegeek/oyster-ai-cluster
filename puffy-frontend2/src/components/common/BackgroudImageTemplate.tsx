export default function BackgroudImageTemplate({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="w-full h-screen flex flex-col items-center absolute top-0 left-0 right-0"
      style={{
        width: "100%",
      }}
    >
      {children}
    </div>
  );
}
