"use client";

import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import { useEffect, useState } from "react";

export default function ShiningBg({
  children,
  className,
  bgClassName,
  color = "#4B7AE6",
}: {
  children: React.ReactNode;
  className?: string;
  bgClassName?: string;
  color?: `#${string}`; // Must start with #
}) {
  const bgColor = `bg-[${color}]`;
  const [isChildrenLoaded, setIsChildrenLoaded] = useState(false);

  useEffect(() => {
    setIsChildrenLoaded(true);
  }, []);

  return (
    <div className={cn("w-full h-full flex items-center justify-center relative", className)}>
      <div className="z-10 flex items-center justify-center">
        {children}
      </div>
      {isChildrenLoaded && (
        <motion.div
          className={cn("w-2/3 h-2/3 absolute -translate-x-1/2 -translate-y-1/2 z-0", bgClassName, bgColor)}
          style={{
            background: `radial-gradient(circle at center, ${color}60 0%, ${color}30 60%, ${color}00 100%)`,
            borderRadius: '50%',
            filter: 'blur(50px)'
          }}
          animate={{
            scale: [0.7, 1.2, 0.7],
            transition: {
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }
          }}
        />
      )}
    </div>
  );
}
