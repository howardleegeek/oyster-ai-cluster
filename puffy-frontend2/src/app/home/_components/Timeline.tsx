import Image from "next/image";
import timelineImage from "@/public/home/timeline.png";
import timelineMobileImage from "@/public/home/timeline-mobile.png";
import { fluidSize } from "@/lib/utils";

export default function Timeline() {
  return (
    <div className="flex flex-col items-center relative">
      <div
        className="flex flex-col items-center absolute top-0 left-0 z-10"
        style={{ gap: fluidSize(12, 24), marginTop: fluidSize(24, 100) }}
      >
        <div
          className="text-center w-11/12 sm:w-3/4 leading-none"
          style={{ fontSize: fluidSize(28, 56), fontWeight: 700 }}
        >
          A MISSION FOR 1.3 BILLION PEOPLE
        </div>
        <div
          className="text-center w-11/12 sm:w-3/4 leading-tight"
          style={{
            fontSize: fluidSize(14, 20),
            marginBottom: fluidSize(40, 80),
          }}
        >
          Over 1.3 billion people worldwide struggle with nicotine addiction.
          Puffy aims to make a positive difference by having quitting into a
          rewarding, supportive experience
        </div>
        <div>
          <TimelineItem
            step={1}
            title="Phase 1"
            points={[
              "Prototype Completed",
              "Puffy Mobile App",
              "Reveal Ecosystem Partnerships",
              "First Batch Public Pre-Sales",
            ]}
          />
          <TimelineItem
            step={2}
            title="Phase 2"
            points={[
              "TGE",
              "Mass Production",
              "Cloudy NFT Release",
              "Puffy App 1.0 Launch",
            ]}
          />
          <TimelineItem
            step={3}
            title="Phase 3"
            points={[
              "Second Batch Public Pre-Sales",
              "Reveal Puffy 2",
              "Puffy App 2.0",
              "Local Distributor Program",
            ]}
          />
          <TimelineItem
            step={4}
            title="Phase 4"
            points={["TBA"]}
            isLast={true}
          />
        </div>
      </div>
      <div className="w-full">
        <Image
          src={timelineImage}
          alt="Timeline showing Puffy's roadmap from Q1 2024 to Q4 2025"
          className="w-full object-cover rounded-4xl hidden sm:block"
          style={{ height: fluidSize(670, 1436) }}
          priority
          quality={100}
        />
        <Image
          src={timelineMobileImage}
          alt="Timeline showing Puffy's roadmap from Q1 2024 to Q4 2025"
          className="w-full object-cover rounded-4xl block sm:hidden"
          style={{ height: fluidSize(670, 1436) }}
          priority
          quality={100}
        />
      </div>
    </div>
  );
}

function TimelineItem({
  step,
  title,
  points,
  isLast = false,
}: {
  step: number;
  title: string;
  points: string[];
  isLast?: boolean;
}) {
  return (
    <div
      className="grid grid-cols-[auto,auto,1fr]"
      style={{ gap: fluidSize(24, 50), width: fluidSize(250, 500) }}
    >
      <div>
        <p
          className="font-semibold leading-none"
          style={{ fontSize: fluidSize(16, 36) }}
        >
          Q{step}
        </p>
        <p className="" style={{ fontSize: fluidSize(12, 20) }}>
          2025
        </p>
      </div>

      <div className="grid grid-rows-[auto,1fr] justify-center">
        <div
          className="bg-black rounded-full"
          style={{ width: fluidSize(7, 16), height: fluidSize(7, 16) }}
        />
        <div className="w-[2px] justify-self-center h-full sm:py-2 py-1">
          <div className="w-[1px] sm:w-[2px] bg-black justify-self-center h-full" />
        </div>
      </div>

      <div>
        <p
          className="font-semibold leading-none"
          style={{
            fontSize: fluidSize(16, 36),
            marginBottom: fluidSize(8, 20),
          }}
        >
          {title}
        </p>
        <ul
          className="list-disc list-inside flex flex-col"
          style={{
            paddingBottom: isLast ? fluidSize(0, 0) : fluidSize(12, 40),
            gap: fluidSize(2, 20),
          }}
        >
          {points.map((point) => (
            <li key={point} style={{ fontSize: fluidSize(12, 20) }}>
              {point}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
