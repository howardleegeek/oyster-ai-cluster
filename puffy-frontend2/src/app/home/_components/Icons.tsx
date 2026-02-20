"use client";

import React from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import Image from "next/image";
import { fluidSize } from "@/lib/utils";

// Import logo images
import AzukiLogo from "@/public/logo/azuki.png";
import BaycLogo from "@/public/logo/bayc.png";
import DegnLogo from "@/public/logo/degn.png";
import DogLogo from "@/public/logo/dog.png";
import DoodlesLogo from "@/public/logo/doodles.png";
import FroganaLogo from "@/public/logo/frogana.png";
import GorbagioLogo from "@/public/logo/gorbagio.png";
import KabutoLogo from "@/public/logo/kabuto.png";
import MadlabsLogo from "@/public/logo/madlabs.png";
import MonkeyLogo from "@/public/logo/monkey.png";
import OysLogo from "@/public/logo/oys.png";
import Player2Logo from "@/public/logo/player2.png";
import PuffpawLogo from "@/public/logo/puffpaw.png";
import SolLogo from "@/public/logo/sol.png";
import SoonLogo from "@/public/logo/soon.png";
import TonfishLogo from "@/public/logo/tonfish.png";

// Logo images array
const logoImages = [
  { src: AzukiLogo, alt: "Azuki Logo" },
  { src: BaycLogo, alt: "BAYC Logo" },
  { src: DegnLogo, alt: "Degn Logo" },
  { src: DogLogo, alt: "Dog Logo" },
  { src: DoodlesLogo, alt: "Doodles Logo" },
  { src: FroganaLogo, alt: "Frogana Logo" },
  { src: GorbagioLogo, alt: "Gorbagio Logo" },
  { src: KabutoLogo, alt: "Kabuto Logo" },
  { src: MadlabsLogo, alt: "Madlabs Logo" },
  { src: MonkeyLogo, alt: "Monkey Logo" },
  { src: OysLogo, alt: "Oys Logo" },
  { src: Player2Logo, alt: "Player Logo" },
  { src: PuffpawLogo, alt: "Puffpaw Logo" },
  { src: SolLogo, alt: "Sol Logo" },
  { src: SoonLogo, alt: "Soon Logo" },
  { src: TonfishLogo, alt: "Tonfish Logo" },
];

export default function Icons() {
  const [ready, setReady] = React.useState(false);

  const sliderSettings = {
    dots: false,
    infinite: true,
    // Continuous marquee-like scroll
    speed: 800,
    cssEase: "ease-out",
    // Let each slide use its natural width instead of forcing a fixed count
    slidesToShow: 1,
    variableWidth: true,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 2000,
    pauseOnHover: true,
    arrows: false,
  };

  return (
    <div
      className="w-full"
      style={{
        paddingTop: 0,
        paddingBottom: 0,
        opacity: ready ? 1 : 0,
        transition: "opacity 0.3s ease-in-out",
      }}
    >
      <Slider {...sliderSettings} onInit={() => setReady(true)}>
        {logoImages.map((logo, index) => (
          <div
            key={index}
            className="inline-flex justify-center items-center px-[35px] md:px-[50px]"
          >
            <Image
              src={logo.src}
              alt={logo.alt}
              height={70}
              width={200}
              className="h-[50px] md:h-[70px] w-auto"
              quality={75}
            />
          </div>
        ))}
      </Slider>
    </div>
  );
}
