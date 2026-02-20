export default function Hero({
  image,
  heroHeight,
  header,
  content,
  footer,
}: {
  image?: React.ReactNode;
  heroHeight?: string;
  header?: React.ReactNode;
  content?: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="w-screen absolute top-0 flex flex-col items-center justify-center">
      <header className="w-full z-10 flex justify-center">{header}</header>
      <div
        className="absolute w-full top-0 left-0 -z-10"
        style={{ height: heroHeight }}
      />
      <div className="absolute top-0 left-0 -z-20 w-full h-full">{image}</div>
      <div
        className="flex flex-col w-full h-full items-center justify-between"
        style={{}}
      >
        <div />
        {content}
        {footer}
      </div>
    </div>
  );
}
