"use client";

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="w-full min-h-screen flex flex-col items-center justify-center gap-4 bg-[#F1F1F1]">
      <p className="text-black/80 text-lg">404 – Page not found</p>
      <Link
        href="/"
        className="rounded-lg bg-black px-4 py-2 text-sm font-medium text-white hover:bg-black/80"
      >
        Go to homepage
      </Link>
    </div>
  );
}
