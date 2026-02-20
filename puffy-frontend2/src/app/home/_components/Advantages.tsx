import Image, { StaticImageData } from "next/image";
import { fluidSize } from "@/lib/utils";
import coachingImage from "@/public/home/coaching.png";
import gamifiedImage from "@/public/home/gamified.png";

export default function Advantages() {
  return (
    <div className="w-full flex flex-col items-center">
      <div
        className="w-full grid grid-cols-1 md:grid-cols-2"
        style={{ gap: 24 }}
      >
        <AdvantageCard
          image={coachingImage}
          title="AI-Driven Coaching"
          description="Your personal AI coach logs your daily data and provides meaningful insights, helping you understand your nicotine intake."
        />
        <AdvantageCard
          image={gamifiedImage}
          title="Gamified Progress"
          description="Turn quitting into a game! Earn stars, unlock achievements, and level up your life as you cut down nicotine."
        />
      </div>
    </div>
  );
}

function AdvantageCard({
  image,
  title,
  description,
}: {
  image: StaticImageData;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl flex flex-col">
      <Image src={image} alt={title} className="w-full" quality={100} />
      <div style={{ height: fluidSize(16, 40) }} />
      <div
        className="font-bold leading-none"
        style={{ fontSize: fluidSize(20, 36) }}
      >
        {title}
      </div>
      <div style={{ height: fluidSize(12, 20) }} />
      <div
        className="text-black leading-tight"
        style={{ fontSize: fluidSize(14, 20) }}
      >
        {description}
      </div>
    </div>
  );
}
