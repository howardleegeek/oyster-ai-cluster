"use client";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

export default function PrimaryButton({
  text,
  redirectUrl,
  onClick,
}: {
  text: string;
  redirectUrl?: string;
  onClick?: () => void;
}) {
  const router = useRouter();
  const handleClick = () => {
    if (redirectUrl) {
      router.push(redirectUrl);
    }
    if (onClick) {
      onClick();
    }
  };

  return (
    <Button
      variant="default"
      size="custom"
      className="text-white px-xl py-2xs rounded-full text-body-base"
      onClick={handleClick}
    >
      {text}
    </Button>
  );
}
