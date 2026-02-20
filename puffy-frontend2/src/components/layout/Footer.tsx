"use client";

import { fluidSize } from "@/lib/utils";
import Image from "next/image";

const label: { name: string; link: string }[] = [
  // {
  //   name: "Privacy Policy",
  //   link: "",
  // },
  // {
  //   name: "Terms & Conditions",
  //   link: "",
  // },
];

export default function Footer() {
  return (
    <div className="w-full bg-transparent">
      <div className="w-full flex items-start justify-between">
        <div className="flex sm:flex-row flex-col items-start sm:items-center sm:gap-[50px]">
          <Image
            src="/puffy-logo.png"
            alt="Puffy Logo"
            width={120}
            height={60}
            style={{ width: fluidSize(90, 120) }}
            quality={100}
          />
          <div className="flex flex-row" style={{ gap: fluidSize(12, 40) }}>
            {label.map((item) => (
              <div
                key={item.name}
                style={{ fontSize: fluidSize(12, 16) }}
                className="cursor-pointer active:scale-95 transition-all"
              >
                {item.name}
              </div>
            ))}
          </div>
        </div>
        <div className="flex flex-row items-start gap-4">
          <Image
            src="/layout/x.svg"
            alt="X"
            width={32}
            height={32}
            style={{ width: fluidSize(28, 32) }}
            className="cursor-pointer active:scale-95 transition-all"
            onClick={() => {
              window.open("https://x.com/puffy_ai", "_blank");
            }}
            quality={100}
          />
          <Image
            src="/layout/tg.svg"
            alt="Telegram"
            width={32}
            height={32}
            style={{ width: fluidSize(28, 32) }}
            className="cursor-pointer active:scale-95 transition-all"
            onClick={() => {
              window.open("https://t.me/puffydotai", "_blank");
            }}
            quality={100}
          />
          <Image
            src="/layout/discord.svg"
            alt="Discord"
            width={32}
            height={32}
            style={{ width: fluidSize(28, 32) }}
            className="cursor-pointer active:scale-95 transition-all"
            onClick={() => {
              window.open("https://discord.gg/jdcj6YamUv", "_blank");
            }}
            quality={100}
          />
        </div>
      </div>
      <div
        className="w-full h-[1px] bg-black opacity-10"
        style={{
          marginTop: fluidSize(12, 24),
          marginBottom: fluidSize(12, 24),
        }}
      />
      <div
        className="w-full text-left text-[#1A1A1A] opacity-40"
        style={{ fontSize: fluidSize(12, 16) }}
      >
        © 2025 All Rights Reserved.
      </div>
    </div>
  );
}
