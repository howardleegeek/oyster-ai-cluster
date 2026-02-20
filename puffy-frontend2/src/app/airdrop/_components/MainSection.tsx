import { fluidSize } from "@/lib/utils";

interface MainSectionProps {
  image: React.ReactNode | null;
  title: string | React.ReactNode | null;
  description: string | React.ReactNode | null;
  button: React.ReactNode | null;
}

export default function MainSection({
  image,
  title,
  description,
  button,
}: MainSectionProps) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center text-pingfang">
      {image && <div className="md:mb-10 mb-6">{image}</div>}
      <div className="w-full flex flex-col items-center justify-center">
        {title && (
          <div
            className="text-black/90 font-semibold text-center"
            style={{ fontSize: fluidSize(24, 32) }}
          >
            {title}
          </div>
        )}
        {description && (
          <div
            className="text-black/50 md:mt-4 mt-2 text-center"
            style={{ fontSize: fluidSize(14, 16) }}
          >
            {description}
          </div>
        )}
        <div className="w-full md:mt-10 mt-6 flex flex-col items-center justify-center">
          {button && button}
        </div>
      </div>
    </div>
  );
}
