"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function MainButton({
  children,
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <Button
      className={cn(
        "text-white md:text-base text-sm rounded-full bg-black py-6 px-12 font-inter min-w-[220px] active:scale-95 transition-all duration-300",
        className
      )}
      variant="default"
      {...props}
    >
      {children}
    </Button>
  );
}
