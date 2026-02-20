import Image from "next/image";
import { fluidSize } from "@/lib/utils";
import podsImage from "@/public/home/pods.png";
import unitImage from "@/public/home/unit.png";
import coinsImage from "@/public/home/coins.png";
import { StaticImageData } from "next/image";

export default function HowItWorks() {
  return (
    <div
      className="w-full flex flex-row overflow-x-auto overflow-y-hidden"
      style={{ gap: fluidSize(12, 24), paddingBottom: fluidSize(12, 24) }}
    >
      <HowItWorksCard
        image={podsImage}
        number={1}
        title="Get your Puffy Device & Pods"
        description="Purchase our NFT device and pods from our marketplace."
      />
      <HowItWorksCard
        image={unitImage}
        number={2}
        title="Connect Your Nicotine Extraction Unit NFT"
        description="Link your NFT with your device. Higher extraction levels mean more rewards, helping you earn more rewards."
      />
      <HowItWorksCard
        image={coinsImage}
        number={3}
        title={
          <p>
            Earn with<br></br> Every Puff
          </p>
        }
        description="Earn rewards with every puff. The lower your nicotine extraction level, the more you earn. Stay within the daily cap to maximize your earnings while maintaining a healthy intake."
      />
    </div>
  );
}

function HowItWorksCard({
  image,
  number,
  title,
  description,
}: {
  image: StaticImageData;
  number: number;
  title: string | React.ReactNode;
  description: string;
}) {
  return (
    <div className="flex flex-col items-start min-w-[241px] w-full">
      <Image src={image} alt={"image"} className="w-full" quality={100} />
      <div style={{ height: fluidSize(16, 40) }} />
      <div
        className="bg-transparent text-black flex items-center justify-center border-[2px] border-black"
        style={{
          width: fluidSize(24, 32),
          height: fluidSize(24, 32),
          fontSize: fluidSize(16, 28),
          borderRadius: fluidSize(8, 12),
          fontWeight: 600,
          padding: fluidSize(12, 24),
        }}
      >
        {number}
      </div>
      <div style={{ height: fluidSize(12, 20) }} />
      <div
        className="font-bold leading-none"
        style={{ fontSize: fluidSize(20, 36) }}
      >
        {title}
      </div>
      <div style={{ height: fluidSize(12, 20) }} />
      <div
        className="text-left leading-tight"
        style={{ fontSize: fluidSize(14, 20) }}
      >
        {description}
      </div>
    </div>
  );
}
