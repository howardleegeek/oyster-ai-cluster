"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";

interface ProductImageGalleryProps {
  images: string[];
  alt: string;
}

export default function ProductImageGallery({
  images,
  alt,
}: ProductImageGalleryProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const thumbContainerRef = useRef<HTMLDivElement>(null);

  // Reset to first image when the images array changes (variant switch)
  useEffect(() => {
    setActiveIndex(0);
  }, [images]);

  const scrollThumbs = useCallback((direction: "left" | "right") => {
    const container = thumbContainerRef.current;
    if (!container) return;
    const scrollAmount = 100;
    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }, []);

  const showThumbnails = images.length > 1;

  return (
    <div className="flex flex-col gap-3 w-full">
      {/* Main image */}
      <div className="w-full rounded-[24px] border border-black/5 bg-[#F5F5F5] flex items-center justify-center overflow-hidden aspect-square">
        <Image
          src={images[activeIndex]}
          alt={alt}
          width={600}
          height={600}
          priority={activeIndex === 0}
          className="w-full h-full object-contain p-6 md:p-10"
        />
      </div>

      {/* Thumbnail strip */}
      {showThumbnails && (
        <div className="relative flex items-center gap-2">
          {/* Left arrow */}
          <button
            type="button"
            onClick={() => scrollThumbs("left")}
            className="shrink-0 w-7 h-7 rounded-full border border-black/10 bg-white flex items-center justify-center hover:bg-black/5 transition-colors"
            aria-label="Scroll thumbnails left"
          >
            <svg
              className="w-3.5 h-3.5 text-black/50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>

          {/* Scrollable thumbnails */}
          <div
            ref={thumbContainerRef}
            className="flex-1 flex gap-2 overflow-x-auto scrollbar-hide"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {images.map((src, idx) => (
              <button
                key={src}
                type="button"
                onClick={() => setActiveIndex(idx)}
                className={`shrink-0 w-[72px] h-[72px] md:w-[80px] md:h-[80px] rounded-xl border-2 overflow-hidden transition-all bg-[#F5F5F5] ${
                  idx === activeIndex
                    ? "border-black ring-1 ring-black/10"
                    : "border-black/10 hover:border-black/30"
                }`}
                aria-label={`View image ${idx + 1}`}
              >
                <Image
                  src={src}
                  alt={`${alt} thumbnail ${idx + 1}`}
                  width={80}
                  height={80}
                  className="w-full h-full object-contain p-1.5"
                />
              </button>
            ))}
          </div>

          {/* Right arrow */}
          <button
            type="button"
            onClick={() => scrollThumbs("right")}
            className="shrink-0 w-7 h-7 rounded-full border border-black/10 bg-white flex items-center justify-center hover:bg-black/5 transition-colors"
            aria-label="Scroll thumbnails right"
          >
            <svg
              className="w-3.5 h-3.5 text-black/50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}
