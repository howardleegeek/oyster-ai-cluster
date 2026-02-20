import Image from "next/image";
import soonImage from "@/public/home/soon-coin.png";
import earthImage from "@/public/home/earth.png";
import gameImage from "@/public/home/game.png";
import puffyImage from "@/public/home/puffy-coin.png";
import { fluidSize } from "@/lib/utils";

export default function Introduction() {
  return (
    <div
      className="flex flex-col items-center"
      style={{ fontSize: fluidSize(36, 102), lineHeight: fluidSize(36, 90) }}
    >
      <h1 className="font-bold text-center flex flex-wrap items-center justify-center gap-1">
        <span
          className="text-[#ED00ED]"
          style={{ marginRight: fluidSize(8, 20) }}
        >
          PUFFY
        </span>
        <span style={{ marginRight: fluidSize(8, 20) }}>IS</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>THE</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>FIRST</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>AI-POWERED</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>VAPE</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>ON</span>
        {/* SOON */}
        <span
          className="inline-flex items-center"
          style={{ marginRight: fluidSize(8, 20) }}
        >
          <span>S</span>
          <Image
            src={soonImage}
            alt="Game controller"
            style={{ width: fluidSize(28, 81) }}
            quality={100}
          />
          <span>ON</span>
        </span>
        <span style={{ marginRight: fluidSize(8, 20) }}>HELPING</span>
        <span>1.3B</span>
        <Image
          src={earthImage}
          alt="Earth"
          style={{ width: fluidSize(28, 81), marginRight: fluidSize(8, 20) }}
          quality={100}
        />
        <span style={{ marginRight: fluidSize(8, 20) }}>SMOKERS</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>QUIT</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>THROUGH</span>
        {/* GAMIFIED */}
        <span
          className="inline-flex items-center"
          style={{ marginRight: fluidSize(8, 20) }}
        >
          <span>GA</span>
          <Image
            src={gameImage}
            alt="Game"
            style={{ width: fluidSize(28, 81) }}
            quality={100}
          />
          <span>IFIED</span>
        </span>
        <span style={{ marginRight: fluidSize(8, 20) }}>TRACKING</span>
        <span style={{ marginRight: fluidSize(8, 20) }}>AND</span>
        {/* REWORDS */}
        <span className="inline-flex items-center">
          <span>REW</span>
          <span className="inline-flex items-center justify-center bg-black rounded-full">
            <Image
              src={puffyImage}
              alt="Puffy"
              style={{ width: fluidSize(28, 81) }}
              quality={100}
            />
          </span>
          <span>RDS.</span>
        </span>
      </h1>
    </div>
  );
}
