"use client";

import Image, { StaticImageData } from "next/image";
import dummyTwitterImage from "@/public/reward-center/dummy-twitter.png";
import { cn, fluidSize } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { redirectToTwitterAuth, TwitterAuthContext } from "@/hooks";
import { User, userLockTwitterUserTwitterLockGet } from "@/types";
import { useContext, useEffect } from "react";
import CoinImage from "@/public/reward-center/coin.gif";
import InvitationLink from "@/app/profile/my-points/_components/InvitationLink";

interface ConnectXElements {
  status:
    | "only shared"
    | "unconnected"
    | "connected but not confirmed"
    | "connected and confirmed";
  title: string | React.ReactNode;
  description: string;
  twitterImage: React.ReactNode | null;
  twitterHandle: string | null;
  buttons: React.ReactNode[];
}

interface StyleOverrides {
  container?: string;
  wrapper?: string;
  title?: string;
  description?: string;
  twitterHandle?: string;
  buttonContainer?: string;
  button?: string;
  imageContainer?: string;
  twitterImageContainer?: string;
  divider?: string;
}

export default function ConnectX({
  showShareButton = true,
  className,
  style,
  styleOverrides = {},
  hasLineWrap = true,
  shareFunction,
  hasSkipButton = true,
  userInfo,
  refetchUserInfo,
  openNftDialog = false,
  isLoading = false,
  coinImage = CoinImage,
  onlyShared = false,
}: {
  showShareButton?: boolean;
  className?: string;
  style?: React.CSSProperties;
  styleOverrides?: StyleOverrides;
  hasLineWrap?: boolean;
  shareFunction?: () => Promise<void> | void;
  hasSkipButton?: boolean;
  userInfo: User;
  refetchUserInfo: () => void;
  openNftDialog?: boolean;
  isLoading?: boolean;
  coinImage?: StaticImageData;
  onlyShared?: boolean;
}) {
  const { status: twitterAuthStatus } = useContext(TwitterAuthContext);
  useEffect(() => {
    if (twitterAuthStatus === "success") {
      refetchUserInfo();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [twitterAuthStatus]);

  const getRedirectUrl = () => {
    const url = new URL(window.location.href);
    url.searchParams.delete("auth_code");
    if (openNftDialog) {
      url.searchParams.set("nft-dialog", "true");
    }
    return url.toString();
  };
  const status:
    | "only shared"
    | "unconnected"
    | "connected but not confirmed"
    | "connected and confirmed" = (() => {
    if (onlyShared) {
      return "only shared";
    }
    if (userInfo?.twitter_id && userInfo?.twitter_locked === true) {
      return "connected and confirmed";
    }
    if (userInfo?.twitter_id && !userInfo?.twitter_locked) {
      return "connected but not confirmed";
    }
    return "unconnected";
  })();

  // Define the elements array directly, not using useMemo
  const elements: ConnectXElements[] = [
    {
      status: "only shared",
      title: hasLineWrap ? <span>Spread the word</span> : "Spread the word",
      description:
        "Earn 100 Puffy Points for every successful mint through your code — your friend earns the same. Only two invites per user. Make them count.",
      twitterImage: (
        <div
          className={cn("flex justify-center", styleOverrides.imageContainer)}
        >
          <Image
            src={coinImage}
            alt="Coin"
            style={{
              width: fluidSize(75, 100),
              height: fluidSize(75, 100),
            }}
          />
        </div>
      ),
      twitterHandle: null,
      buttons: [
        <div key="share-button" className="flex flex-col gap-6 mt-4">
          {userInfo.referral_code && (
            <InvitationLink
              referralCode={userInfo.referral_code}
              containerClassName="flex-col md:flex-col justify-center items-center gap-2"
              showDescription={false}
            />
          )}
          <CustomButton
            className={styleOverrides.button}
            onClick={() => {
              shareFunction?.();
            }}
          >
            <XSvg />
            Share
          </CustomButton>
        </div>,
      ],
    },
    {
      status: "unconnected",
      title: hasLineWrap ? <span>Spread the word</span> : "Spread the word",
      description:
        "Earn 100 Puffy Points for every successful mint through your code — your friend earns the same. Only two invites per user. Make them count.",
      twitterImage: (
        <div
          className={cn("flex justify-center", styleOverrides.imageContainer)}
        >
          <Image
            src={coinImage}
            alt="Coin"
            style={{
              width: fluidSize(75, 100),
              height: fluidSize(75, 100),
            }}
          />
        </div>
      ),
      twitterHandle: null,
      buttons: [
        <div key="connect-button">
          <CustomButton
            className={styleOverrides.button}
            onClick={() => {
              redirectToTwitterAuth(getRedirectUrl());
            }}
          >
            <XSvg />
            Connect
          </CustomButton>
          {hasSkipButton && (
            <button
              className="text-[#1a1a1a] w-full text-center md:mt-[18px] mt-[10px] active:scale-95 transition-all duration-300"
              onClick={() => {
                shareFunction?.();
              }}
              style={{
                fontSize: fluidSize(8, 12),
              }}
            >
              Share Without Earning
            </button>
          )}
        </div>,
      ],
    },
    {
      status: "connected but not confirmed",
      title: "This Action Can't Be Undone",
      description:
        "Each wallet can be linked to only one X account — permanently. Are you sure you want to link this X account to Puffy?",
      twitterImage: (
        <div
          className={cn("flex justify-center", styleOverrides.imageContainer)}
        >
          <Image
            src={userInfo?.twitter_icon_url || dummyTwitterImage}
            alt="X logo"
            style={{
              width: fluidSize(50, 75),
              height: fluidSize(50, 75),
            }}
            width={75}
            height={75}
            className="rounded-full"
          />
        </div>
      ),
      twitterHandle: userInfo?.twitter_name || "",
      buttons: [
        <CustomButton
          key="switch-account-button"
          className={cn(
            "bg-white text-black border border-black/10",
            styleOverrides.button
          )}
          onClick={() => {
            redirectToTwitterAuth(getRedirectUrl());
          }}
        >
          Switch Account
        </CustomButton>,
        <CustomButton
          key="link-account-button"
          className={styleOverrides.button}
          onClick={async () => {
            await userLockTwitterUserTwitterLockGet();
            refetchUserInfo();
          }}
        >
          Link My X Account
        </CustomButton>,
      ],
    },
    {
      status: "connected and confirmed",
      title: hasLineWrap ? <span>Spread the word</span> : "Spread the word",
      description:
        "Earn 100 Puffy Points for every successful mint through your code — your friend earns the same. Only two invites per user. Make them count.",
      twitterImage: (
        <div
          className={cn("flex justify-center", styleOverrides.imageContainer)}
        >
          <Image
            src={userInfo?.twitter_icon_url || dummyTwitterImage}
            alt="X logo"
            style={{
              width: fluidSize(50, 75),
              height: fluidSize(50, 75),
            }}
            width={75}
            height={75}
            className="rounded-full"
          />
        </div>
      ),
      twitterHandle: userInfo?.twitter_name || "",
      buttons: showShareButton
        ? [
            <CustomButton
              key="share-button"
              className={styleOverrides.button}
              onClick={() => {
                shareFunction?.();
              }}
            >
              {isLoading ? (
                "Copying Image..."
              ) : (
                <>
                  <XSvg />
                  Share Your Love
                </>
              )}
            </CustomButton>,
          ]
        : [],
    },
  ];

  return (
    <div
      className={cn(
        "flex flex-col items-center w-full h-full justify-center font-pingfang",
        styleOverrides.wrapper,
        className
      )}
      style={style}
    >
      {elements.map(
        (element, index) =>
          status === element.status && (
            <Component
              key={index}
              {...element}
              styleOverrides={styleOverrides}
            />
          )
      )}
    </div>
  );
}

function XSvg() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M14 14L9.30724 7.00618L9.31525 7.01273L13.5465 2H12.1325L8.68564 6.08L5.94841 2H2.2401L6.62125 8.52965L6.62072 8.5291L2 14H3.41396L7.24607 9.46073L10.2917 14H14ZM5.38817 3.09091L11.9724 12.9091H10.8519L4.26235 3.09091H5.38817Z"
        fill="white"
      />
    </svg>
  );
}

function CustomButton({
  children,
  onClick,
  className,
}: {
  children: React.ReactNode;
  onClick: () => void;
  className?: string;
}) {
  return (
    <Button
      className={cn(
        "w-full h-full bg-black text-white rounded-full active:scale-95 transition-all duration-300 py-[12px]",
        className
      )}
      onClick={onClick}
      style={{
        fontWeight: 400,
        fontSize: fluidSize(10, 14),
      }}
    >
      {children}
    </Button>
  );
}

function Component({
  title,
  description,
  twitterImage,
  twitterHandle,
  buttons,
  styleOverrides = {},
}: ConnectXElements & { styleOverrides?: StyleOverrides }) {
  return (
    <div className={cn("flex flex-col items-center", styleOverrides.container)}>
      <div
        className={cn(
          "flex flex-col items-center",
          styleOverrides.twitterImageContainer
        )}
      >
        {twitterImage}
        {twitterHandle && (
          <div
            className={cn(
              "text-center font-semibold text-black leading-tight md:mt-[12px] mt-[0px]",
              styleOverrides.twitterHandle
            )}
            style={{
              fontSize: fluidSize(24, 32),
            }}
          >
            {twitterHandle}
          </div>
        )}
      </div>
      <div
        className={cn(
          "w-full h-[1px] bg-black/10 my-[20px]",
          styleOverrides.divider
        )}
      />
      <p
        className={cn(
          "text-center font-medium leading-tight",
          styleOverrides.title
        )}
        style={{
          fontSize: fluidSize(16, 20),
        }}
      >
        {title}
      </p>
      <div
        style={{
          height: fluidSize(6, 12),
        }}
      />
      <p
        className={cn(
          "text-center font-normal text-black/50 leading-tight",
          styleOverrides.description
        )}
        style={{
          fontSize: fluidSize(10, 14),
        }}
      >
        {description}
      </p>
      {buttons.length > 0 && (
        <>
          <div
            style={{
              height: fluidSize(12, 20),
            }}
          />
          <div
            className={cn(
              "w-full flex flex-row gap-[8px] md:gap-[16px]",
              styleOverrides.buttonContainer
            )}
          >
            {buttons.map((button, index) => (
              <div key={index} className="flex-1">
                {button}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
