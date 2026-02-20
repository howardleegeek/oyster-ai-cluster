"use client";

import ConnectWalletButton from "@/components/features/ConnectWalletButton";
import { fluidSize } from "@/lib/utils";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useCart } from "@/contexts/CartContext";

export default function Header() {
  const router = useRouter();
  const { itemCount } = useCart();

  return (
    <div className="w-full flex items-center justify-between">
      <Image
        src="/puffy-logo.png"
        alt="Puffy Logo"
        width={238}
        height={64}
        style={{
          width: fluidSize(90, 120),
        }}
        priority
        className="cursor-pointer"
        onClick={() => {
          router.push("/");
        }}
        quality={100}
      />
      <div className="flex items-center gap-[12px] sm:gap-[40px]">
        <div
          style={{ fontSize: fluidSize(12, 16) }}
          className="cursor-pointer font-normal active:scale-95 transition-all text-right leading-none"
          onClick={() => {
            router.push("/device");
          }}
        >
          Buy Device
        </div>
        <div
          style={{ fontSize: fluidSize(12, 16) }}
          className="cursor-pointer font-normal active:scale-95 transition-all text-right leading-none"
          onClick={() => {
            router.push("/pods");
          }}
        >
          Smart Pods
        </div>
        <button
          type="button"
          onClick={() => router.push("/cart")}
          style={{ fontSize: fluidSize(12, 16) }}
          className="cursor-pointer font-normal active:scale-95 transition-all text-right leading-none flex items-center gap-1 bg-transparent border-0 p-0 text-inherit"
          aria-label={itemCount > 0 ? `Cart, ${itemCount} items` : "Cart"}
        >
          Cart
          {itemCount > 0 && (
            <span className="inline-flex items-center justify-center min-w-[18px] h-[18px] rounded-full bg-black text-white text-xs font-medium px-1">
              {itemCount > 99 ? "99+" : itemCount}
            </span>
          )}
        </button>
        <div
          style={{ fontSize: fluidSize(12, 16) }}
          className="cursor-pointer font-normal active:scale-95 transition-all text-right leading-none"
          onClick={() => {
            router.push("/airdrop");
          }}
        >
          Puffy Pass Whitelist
        </div>
        <ConnectWalletButton />
        {/* <ConnectWalletButton fontSize={fluidSize(14, 20)} /> */}
        {/* <div className="block sm:hidden">
          {labels.length > 0 && <DropDownList items={labels} />}
        </div> */}
      </div>
    </div>
  );
}
