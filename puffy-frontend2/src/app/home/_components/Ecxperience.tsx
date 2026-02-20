import { fluidSize } from "@/lib/utils";
import Image from "next/image";
import twopodsImage from "@/public/home/two-pods.png";
import appImage from "@/public/home/app.png";
import deviceImage from "@/public/home/device.png";
import securedImage from "@/public/home/secured.png";
import insightsImage from "@/public/home/insights.png";
import { StaticImageData } from "next/image";

export default function Experience() {
  return (
    <div className="flex flex-col w-full">
      <div
        className="grid grid-col-1 sm:grid-cols-2 "
        style={{ gap: fluidSize(12, 24) }}
      >
        <Image
          src={twopodsImage}
          alt="Experience"
          width={668}
          height={890}
          className="w-full"
          quality={100}
        />
        <Image
          src={appImage}
          alt="Experience"
          width={668}
          height={890}
          className="w-full"
          quality={100}
        />
      </div>
      <div style={{ height: fluidSize(12, 24) }} />
      <div
        className="w-full flex flex-row overflow-x-auto overflow-y-hidden"
        style={{ gap: fluidSize(12, 24), paddingBottom: fluidSize(12, 24) }}
      >
        <ExperienceCard
          image={deviceImage}
          title="Smart & Fun Vape Device"
          description="Customize your experience with adjustable settings, track your nicotine intake and progress, and stay connected with peers on Discord. You can also earn rewards while maintaining a healthy track."
        />
        <ExperienceCard
          image={securedImage}
          title="Puffy Secured Pods™"
          description="Each pod is equipped with a built-in security chip that ensures authenticity and tracks all PUFFY records. This guarantees an uncompromised vaping experience while maintaining accurate data for your progress."
        />
        <ExperienceCard
          image={insightsImage}
          title="AI Insights via Puffy App"
          description="Track your nicotine reduction in real time, analyze your vaping patterns, and receive personalized progress analysis. The Puffy App adapts to your habits to provide the optimum nicotine reduction plan."
        />
      </div>
    </div>
  );
}

function ExperienceCard({
  image,
  title,
  description,
}: {
  image: StaticImageData;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl flex flex-col min-w-[241px] w-full">
      <Image
        src={image}
        alt={title}
        width={437}
        height={582}
        className="w-full h-auto"
        quality={100}
      />
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
