"use client";

import { ArrowRightOutlined } from "@ant-design/icons";
import Image from "next/image";

interface CheckButtonProps {
  icon: string;
  title: string;
  className?: string;
  onClick?: () => void;
  arrowClassName?: string;
  titleClassName?: string;
}

export default function CheckButton({
  icon = "",
  title,
  className = "",
  arrowClassName = "",
  titleClassName = "",
  onClick,
}: CheckButtonProps) {
  return (
    <div
      className={`w-[280px] md:p-4 p-2 bg-[#F1F1F1] rounded-full flex items-center gap-3 cursor-pointer active:scale-95 transition-all ${className}`}
      onClick={onClick}
    >
      <Image
        src={icon}
        alt={title}
        className="rounded-full"
        width={34}
        height={34}
      />
      <span
        className={`flex-1 text-sm text-black-900 font-normal ${titleClassName}`}
      >
        {title}
      </span>
      <ArrowRightOutlined className={arrowClassName} />
    </div>
  );
}
