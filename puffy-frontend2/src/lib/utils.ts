import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fluidSize(
  minSize: number,
  maxSize: number,
  minScreen: number = 320,
  maxScreen: number = 1440
): string {
  // Ensure all input values are valid numbers
  if (
    [minSize, maxSize, minScreen, maxScreen].some(
      (num) => !Number.isFinite(num)
    )
  ) {
    throw new Error("All parameters must be valid numbers");
  }

  // // Ensure max values are greater than min values
  // if (minSize > maxSize || minScreen > maxScreen) {
  //   throw new Error("Max values must be greater than min values");
  // }

  // Calculate slope (vw)
  const slope = ((maxSize - minSize) / (maxScreen - minScreen)) * 100;

  // Calculate base pixel value (y-intercept)
  const intercept = minSize - (slope * minScreen) / 100;

  // Round to 4 decimal places to avoid long decimals
  const roundedSlope = Number(slope.toFixed(4));
  const roundedIntercept = Number(intercept.toFixed(4));

  // Simplify output format if intercept is 0
  const interceptStr =
    roundedIntercept === 0
      ? ""
      : roundedIntercept > 0
      ? ` + ${roundedIntercept}px`
      : ` - ${Math.abs(roundedIntercept)}px`;

  // Build clamp function string
  return `clamp(${minSize}px, ${roundedSlope}vw${interceptStr}, ${maxSize}px)`;
}

export function formatTime(time: number) {
  if (time <= 0) {
    return "";
  }
  const days = Math.floor(time / (24 * 60 * 60));
  const hours = Math.floor((time % (24 * 60 * 60)) / (60 * 60));
  const minutes = Math.floor((time % (60 * 60)) / 60);
  const seconds = time % 60;
  const formatNumber = (num: number) => (num < 10 ? `0${num}` : num);
  return `${days}d : ${formatNumber(hours)}h : ${formatNumber(
    minutes
  )}m : ${formatNumber(seconds)}s`;
}
