"use client";

import Image from "next/image";
import { fluidSize } from "@/lib/utils";
import Hero from "@/components/common/Hero";
import { HEADER_HEIGHT, HEADER_HEIGHT_MOBILE } from "@/components/layout/const";
import cloudImage from "@/public/home/cloud.png";
import backgroundImage from "@/public/home/background.png";
import backgroundLargeImage from "@/public/home/background-large.png";
import useWindow from "@/hooks/common/useWindow";
import { useState, useEffect } from "react";
import heroImage from "@/public/home/hero-image.png";
import heroItemImage from "@/public/home/hero-item.png";
import heroItem2Image from "@/public/home/hero-item-2.png";
import heroStarsImage from "@/public/home/stars.png";

export default function HomeHero() {
  const { width } = useWindow();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!document) return;
      const rect = document.getElementById('follow-container')?.getBoundingClientRect();
      if (!rect) return;

      // Normalize mouse position to range [-1, 1]
      const x = Math.max(-1, Math.min(1, ((e.clientX - rect.left) / rect.width) * 2 - 1));
      const y = Math.max(-1, Math.min(1, ((e.clientY - rect.top) / rect.height) * 2 - 1));

      setMousePosition({ x, y });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const moveX = mousePosition.x * 8;
  const moveY = mousePosition.y * 8;
  const rotateX = mousePosition.y * 4;
  const rotateY = -mousePosition.x * 4;

  return (
    <div
      className="w-full"
      style={{
        height: fluidSize(
          432 - HEADER_HEIGHT_MOBILE - 16 + 50,
          980 - HEADER_HEIGHT - 24 + 80
        ),
      }}
    >
      <Hero
        header={<div style={{ height: fluidSize(66 + 40, 96 + 50) }} />}
        image={
          <Image
            src={width > 1440 ? backgroundLargeImage : backgroundImage}
            alt="Reward Center Background"
            className="object-cover w-full"
            style={{
              height: fluidSize(432 + 60, 980 + 90),
            }}
            priority
            quality={100}
          />
        }
        content={
          <div className="flex flex-col items-center justify-center">
            <HeroTitle />
            <div id="follow-container" className="relative w-full transition-transform duration-200 ease-out overflow-hidden" style={{
              transform: `
                  translate(${moveX}px, ${moveY}px)
                  rotateX(${rotateX}deg)
                  rotateY(${rotateY}deg)
                `,
              perspective: '1000px'
            }}>
              <Image
                src={heroItemImage}
                alt="Puffy Logo"
                className="absolute bottom-0"
                style={{
                  width: fluidSize(79, 169),
                  left: fluidSize(40, 140),
                }}
                priority
                quality={100}
              />
              <Image
                src={heroItem2Image}
                alt="Puffy Logo"
                className="absolute z-10"
                style={{
                  width: fluidSize(150, 359),
                  right: fluidSize(-40, 10),
                  top: fluidSize(20, 20),
                }}
                priority
                quality={100}
              />
              <Image
                src={heroStarsImage}
                alt="Puffy Logo"
                className="absolute top-0"
                style={{
                  width: fluidSize(76, 172),
                  left: fluidSize(0, 40),
                }}
                priority
                quality={100}
              />
              <div
                className="w-full h-full  flex items-center justify-center"

              >
                <Image
                  src={heroImage}
                  alt="Puffy Logo"
                  style={{
                    width: fluidSize(234, 499),
                  }}
                  priority
                  quality={100}
                />
              </div>
            </div>
          </div>
        }
      />
    </div>
  );
}

function HeroTitle() {
  return (
    <div
      className="flex flex-col items-center p-2"
      style={{ fontSize: fluidSize(25, 72), lineHeight: fluidSize(26, 72) }}
    >
      <h1 className="font-bold text-center flex flex-col items-center justify-center" style={{ lineHeight: fluidSize(26, 67) }}>
        <div className="flex items-center gap-1">
          MEET PUFFY{" "}
          <Image
            alt="cloud"
            src={cloudImage}
            style={{ width: fluidSize(33, 90) }}
            priority
            quality={100}
          />
        </div>
        <span>YOUR AI COMPANION TO</span>
        <span>QUIT NICOTINE</span>
      </h1>
    </div>
  );
}
