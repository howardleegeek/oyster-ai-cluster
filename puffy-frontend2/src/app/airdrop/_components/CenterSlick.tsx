"use client";

import React, { useState, useEffect } from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import Image from "next/image";
import { motion } from "framer-motion";
import { useGetCampaignsCampaignsGet } from "@/types/api/reward-center-api/reward-center-api";
import { fluidSize } from "@/lib/utils";

export default function CenterSlick() {
  // fetch campaigns info from server
  const { data: campaigns } = useGetCampaignsCampaignsGet({
    query: {
      enabled: true,
    },
  });
  const validCampaigns = campaigns?.filter(
    (campaign) => campaign.logo_url && campaign.promote_image_url
  );
  const [currentSlide, setCurrentSlide] = useState(0);

  // Calculate actual width based on viewport
  const getActualWidth = () => {
    if (typeof window === "undefined") return 280;
    const vw = window.innerWidth;
    const minSize = 280;
    const maxSize = 400;
    const minScreen = 320;
    const maxScreen = 2160;

    const slope = ((maxSize - minSize) / (maxScreen - minScreen)) * 100;
    const intercept = minSize - (slope * minScreen) / 100;
    const calculated = (slope * vw) / 100 + intercept;

    return Math.max(minSize, Math.min(maxSize, calculated));
  };

  const [baseWidthNum, setBaseWidthNum] = useState(getActualWidth());

  useEffect(() => {
    const handleResize = () => {
      setBaseWidthNum(getActualWidth());
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const getCardWidth = (
    slideIndex: number,
    currentIndex: number,
    totalSlides: number
  ) => {
    const distance = Math.min(
      Math.abs(slideIndex - currentIndex),
      totalSlides - Math.abs(slideIndex - currentIndex)
    );

    let scale;
    switch (distance) {
      case 0:
        scale = 1; // center - 100%
        break;
      case 1:
        scale = 0.9; // next to center - 90%
        break;
      case 2:
        scale = 0.85; // second from center - 85%
        break;
      case 3:
        scale = 0.8; // third from center - 80%
        break;
      default:
        scale = 0.75; // further away - 75%
    }

    return baseWidthNum * scale;
  };

  const settings = {
    className: "center",
    centerMode: true,
    infinite: true,
    variableWidth: true,
    speed: 800,
    autoplay: true,
    autoplaySpeed: 2000,
    pauseOnHover: false,
    pauseOnFocus: false,
    swipe: false,
    draggable: false,
    touchMove: false,
    cssEase: "ease-out",
    beforeChange: (oldIndex: number, newIndex: number) => {
      setCurrentSlide(newIndex);
    },
  };

  const imageHeight = fluidSize(320, 456, 365, 2460);

  return (
    <div
      className="w-full mt-8 overflow-hidden [&_.slick-list]:!flex [&_.slick-list]:!items-end [&_.slick-track]:!flex [&_.slick-track]:!items-end"
      style={{ height: imageHeight }}
    >
      <Slider {...settings}>
        {validCampaigns?.map((campaign, index) => {
          const cardWidth = getCardWidth(
            index,
            currentSlide,
            validCampaigns.length
          );

          return (
            <div key={index} className="mx-2">
              <motion.div
                className="rounded-lg flex flex-col gap-2 justify-end"
                animate={{
                  width: cardWidth,
                  height: imageHeight,
                }}
                initial={false}
                transition={{
                  duration: 0.8,
                  ease: "easeOut",
                }}
              >
                <div className="flex flex-row items-center gap-2">
                  <Image
                    src={campaign.logo_url || ""}
                    alt={`Logo ${index}`}
                    width={20}
                    height={20}
                    className="rounded-full object-contain w-5 h-5"
                  />
                  <p className="text-black text-sm font-bold">
                    {campaign.name}
                  </p>
                </div>
                <div className="w-full">
                  <Image
                    src={campaign.promote_image_url || ""}
                    alt={`NFT ${index}`}
                    width={560}
                    height={560}
                    className="rounded-lg object-cover w-full aspect-square"
                  />
                </div>
              </motion.div>
            </div>
          );
        })}
      </Slider>
    </div>
  );
}
