"use client";

import { fluidSize } from "@/lib/utils";
import { forwardRef } from "react";

interface NFTDisplayProps {
  nftId: string;
  description: string;
  posterUrl: string;
  videoUrl: string;
  isCoping: boolean;
}

const NFTDisplay = forwardRef<HTMLDivElement, NFTDisplayProps>(
  ({ nftId, description, posterUrl, videoUrl, isCoping }, ref) => {
    return (
      <div
        className="w-full flex flex-col md:flex-row items-center justify-between"
        ref={ref}
      >
        <div
          className="w-full flex flex-col items-center"
          style={{
            padding: fluidSize(14, 20),
            borderRadius: isCoping ? 0 : fluidSize(16, 24),
            backgroundColor: "#eef0f2",
          }}
        >
          <div
            className="w-full flex flex-col items-start font-semibold text-[#ED00ED] mb-1"
            style={{ fontSize: fluidSize(8, 10) }}
          >
            {description}
          </div>
          {isCoping ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={posterUrl}
              className="w-full h-full"
              style={{
                aspectRatio: "1684/1440",
              }}
              alt="NFT"
            />
          ) : (
            <div
              className="w-full overflow-hidden"
              style={{
                aspectRatio: "1684/1440",
              }}
            >
              <video
                autoPlay
                poster={posterUrl}
                muted
                loop
                className="w-full h-full"
                playsInline
                preload="auto"
                style={{
                  aspectRatio: "1684/1440",
                  transform: "scale(1.007)",
                }}
              >
                {videoUrl && <source src={videoUrl} type="video/mp4" />}
              </video>
            </div>
          )}
          <div
            className="w-full flex flex-row items-center justify-end gap-1"
            style={{
              marginTop: fluidSize(12, 24),
            }}
          >
            <div
              className="text-black leading-none text-right flex flex-col items-end justify-center"
              style={{
                fontSize: fluidSize(7, 10),
                letterSpacing: "-0.05em",
                fontWeight: 800,
              }}
            >
              <div>PUFFY</div>
              <div>PASS WL</div>
            </div>
            <div
              className="text-black font-bold leading-none"
              style={{ fontSize: fluidSize(14, 20) }}
            >
              #{nftId.replace("#", "")}
            </div>
          </div>
        </div>
      </div>
    );
  }
);

NFTDisplay.displayName = "NFTDisplay";

export default NFTDisplay;
