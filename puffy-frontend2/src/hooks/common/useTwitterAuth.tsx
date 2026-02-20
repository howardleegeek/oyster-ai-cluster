"use client";

import { useQuery } from "@tanstack/react-query";
import { useState, useEffect, createContext, useContext } from "react";
import { useCampaign } from "../reward-center/useCampaign";
import { useWalletLogin } from "./useWalletLogin";
import { userTwitterOauthUserTwitterOauthPost } from "@/types";
import { useRouter } from "next/navigation";

// Twitter OAuth URL generator functions
function percentEncodeRFC3986(val: string): string {
  return encodeURIComponent(val).replace(
    /[!'()*]/g,
    (char) => `%${char.charCodeAt(0).toString(16).toUpperCase()}`
  );
}

function generateTwitterAuthorizeUrl(redirectUrl: string): string {
  const baseUrl = "https://x.com/i/oauth2/authorize";
  const params = {
    response_type: "code",
    client_id: process.env.NEXT_PUBLIC_X_CLIENT_ID as string,
    redirect_uri: clearUrlParams(redirectUrl),
    scope: "users.read tweet.read",
    state: "state",
    code_challenge: "challenge",
    code_challenge_method: "plain",
  };

  console.log("params", params);

  const encodedParams = Object.keys(params)
    .map((key) => {
      // Fix the type issue by using type assertion for key
      const typedKey = key as keyof typeof params;
      return `${percentEncodeRFC3986(key)}=${percentEncodeRFC3986(
        params[typedKey]
      )}`;
    })
    .join("&");

  return `${baseUrl}?${encodedParams}`;
}

// Redirect to Twitter auth function
export function redirectToTwitterAuth(redirectUrl: string): void {
  const authorizeUrl = generateTwitterAuthorizeUrl(redirectUrl);
  window.location.href = authorizeUrl;
}

export const TwitterAuthContext = createContext<{
  status: "error" | "success" | "pending";
}>({
  status: "pending",
});

export function useTwitterAuth() {
  const context = useContext(TwitterAuthContext);
  if (!context) {
    throw new Error("useTwitterAuth must be used within TwitterAuthProvider");
  }
  return context;
}

export function TwitterAuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [accessCode, setAccessCode] = useState<string | null>(null);
  const { refetchUserInfo } = useCampaign();
  const { status: authStatus } = useWalletLogin();
  const router = useRouter();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    setAccessCode(code);

    // Fix broken URL with multiple question marks
    const currentUrl = window.location.href;
    if (currentUrl.includes("?error=")) {
      const fixedUrl = currentUrl.replace(/(\?[^?]*)(\?)/, "$1&");
      console.log("fixedUrl", fixedUrl);
      window.history.replaceState({}, "", fixedUrl);
    }
  }, []);

  const { data, status } = useQuery({
    queryKey: ["twitter-auth", accessCode],
    queryFn: () => {
      return userTwitterOauthUserTwitterOauthPost({
        auth_code: accessCode as string,
        redirect_url: clearUrlParams(window.location.href),
      });
    },
    enabled: accessCode !== null && authStatus === "authenticated",
  });

  useEffect(() => {
    if (data?.status === "success") {
      // Refresh current page and discard code and state parameters
      const url = new URL(window.location.href);
      url.searchParams.delete("code");
      url.searchParams.delete("state");
      router.push(url.pathname + (url.search !== "?" ? url.search : ""));
    }
  }, [data, refetchUserInfo]);

  return (
    <TwitterAuthContext.Provider value={{ status }}>
      {children}
    </TwitterAuthContext.Provider>
  );
}

function clearUrlParams(url: string) {
  const urlObj = new URL(url);
  urlObj.searchParams.delete("code");
  urlObj.searchParams.delete("state");
  return urlObj.toString();
}
