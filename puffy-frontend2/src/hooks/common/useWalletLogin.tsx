"use client";

import { useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";
import { useMutation } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useState } from "react";
import bs58 from "bs58";
import {
  signInSignInGet,
  useVerifyVerifyPost,
  eligibleSignInCampaignsCampaignIdEligibleSignInGet,
  eligibleVerifyCampaignsCampaignIdEligibleVerifyPost,
} from "@/types/api/reward-center-api/reward-center-api";
import { SolSignProof } from "@/types/api/fastAPI.schemas";
import { axiosInstance } from "@/lib/custom-instance";

const PUFFY_TOKEN_KEY = "puffy_token_campaign";

export type AuthStatus =
  | "unchecked"
  | "loading"
  | "disconnected"
  | "connected"
  | "authenticated"
  | null;

interface WalletLoginContextType {
  logout: () => void;
  signin: (options?: {
    authCode?: string;
    campaignId?: number;
  }) => Promise<void>;
  login: (options?: {
    authCode?: string;
    campaignId?: number;
  }) => Promise<void>;
  status: AuthStatus;
  eligibleVerificationStatus: "idle" | "pending" | "success" | "error";
  eligibleVerificationError?: Error | null;
  resetEligibleVerification: () => void;
  signinStatus: "idle" | "pending" | "success" | "error";
  signinError?: Error | null;
  resetSignin: () => void;
}

const WalletLoginContext = createContext<WalletLoginContextType>({
  logout: () => {},
  signin: async () => {},
  login: async () => {},
  status: "unchecked",
  eligibleVerificationStatus: "idle",
  eligibleVerificationError: null,
  resetEligibleVerification: () => {},
  signinStatus: "idle",
  signinError: null,
  resetSignin: () => {},
});

export const useWalletLogin = () => {
  const context = useContext(WalletLoginContext);
  if (!context) {
    throw new Error(
      "useWalletLoginStore must be used within WalletLoginProvider"
    );
  }
  return context;
};

export const WalletLoginProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { publicKey, disconnect, disconnecting, signMessage } = useWallet();
  const { setVisible } = useWalletModal();
  const [authStatus, setAuthStatus] = useState<AuthStatus>("unchecked");
  const [triggerLogin, setTriggerLogin] = useState(false);
  const [loginOptions, setLoginOptions] = useState<{
    authCode?: string;
    campaignId?: number;
  }>();

  // Sign-in mutations
  const signinMutation = useMutation({
    mutationFn: async (options?: {
      campaignId?: number;
      authCode?: string;
    }) => {
      if (options?.campaignId && options?.authCode) {
        return await eligibleSignInCampaignsCampaignIdEligibleSignInGet(
          options.campaignId,
          {
            headers: {
              Authorization: `Bearer ${options.authCode}`,
            },
          }
        );
      }
      return await signInSignInGet();
    },
    onError: (error) => {
      setAuthStatus(publicKey ? "connected" : "disconnected");
      throw error;
    },
  });

  // General verify mutation
  const { mutateAsync: verifyGeneral } = useVerifyVerifyPost({
    mutation: {
      onSuccess: (data) => {
        if (data.token) {
          localStorage.setItem(PUFFY_TOKEN_KEY, data.token);
          axiosInstance.defaults.headers.common["Authorization"] =
            `Bearer ${data.token}`;
          setAuthStatus(publicKey ? "authenticated" : "disconnected");
        }
      },
      onError: () => {
        setAuthStatus(publicKey ? "connected" : "disconnected");
      },
    },
    request: {
      headers: {
        Authorization: `Bearer `,
      },
    },
  });

  const verifyEligible = useMutation({
    mutationFn: async ({
      campaignId,
      data,
      authCode,
    }: {
      campaignId: number;
      data: { session_id: string; data: SolSignProof };
      authCode: string;
    }) => {
      return await eligibleVerifyCampaignsCampaignIdEligibleVerifyPost(
        campaignId,
        data,
        {
          headers: {
            Authorization: `Bearer ${authCode}`,
          },
        }
      );
    },
    onSuccess: (data) => {
      if (data.token) {
        localStorage.setItem(PUFFY_TOKEN_KEY, data.token);
        axiosInstance.defaults.headers.common["Authorization"] =
          `Bearer ${data.token}`;
        setAuthStatus(publicKey ? "authenticated" : "disconnected");
      }
    },
  });

  // Unified verify function
  const verify = async (
    data: { session_id: string; data: SolSignProof },
    options?: { campaignId?: number; authCode?: string }
  ) => {
    if (options?.campaignId && options?.authCode) {
      return await verifyEligible.mutateAsync({
        campaignId: options.campaignId,
        data,
        authCode: options.authCode,
      });
    }
    return await verifyGeneral({ data });
  };

  useEffect(() => {
    const handleLogin = async () => {
      if (publicKey && triggerLogin) {
        try {
          await login(loginOptions);
          setTriggerLogin(false);
        } catch (error) {
          // Handle login error - reset trigger so user can retry
          setTriggerLogin(false);
          console.error("Auto-login failed after wallet connection:", error);
        }
      }
    };
    handleLogin();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [publicKey, triggerLogin]);

  // For users who have not connected wallet
  const signin = async (options?: {
    authCode?: string;
    campaignId?: number;
    errorCallback?: () => void;
  }) => {
    try {
      // Reset verification status when signin is called
      verifyEligible.reset();

      // console.log("signin", publicKey);
      if (!publicKey) {
        setVisible(true);
        setLoginOptions(options);
        setTriggerLogin(true);
        return;
      }

      // If wallet is connected, proceed with login
      await login(options);
    } catch (error) {
      setTriggerLogin(false);
      console.error("signin error", error);
    }
  };

  // For users who have connected wallet
  const login = async (options?: {
    authCode?: string;
    campaignId?: number;
  }) => {
    if (!publicKey) {
      setVisible(true);
      return;
    }

    try {
      // Reset verification status when login is called
      verifyEligible.reset();

      setAuthStatus("loading");
      const signinData = await signinMutation.mutateAsync(options);
      const message = signinData.message;

      if (!signMessage || !message) {
        throw new Error("Failed to get message to sign");
      }
      const signature = await signMessage(new TextEncoder().encode(message));

      const solSignProof: SolSignProof = {
        signature: bs58.encode(signature),
        address: publicKey.toString(),
      };

      await verify(
        {
          session_id: signinData.session_id,
          data: solSignProof,
        },
        options
      );
    } catch (error) {
      // Reset auth status on error so user can retry
      setAuthStatus(publicKey ? "connected" : "disconnected");
      throw error;
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (!publicKey) {
        setAuthStatus("disconnected");
        return;
      }

      // Don't override status if already loading or authenticated
      if (authStatus === "loading" || authStatus === "authenticated") {
        return;
      }

      setAuthStatus("connected");
      // read token from localStorage
      const token = localStorage.getItem(PUFFY_TOKEN_KEY);
      // verify the token
      if (token) {
        const tokenPublicKey = parseTokenToPublicKey(token);
        if (tokenPublicKey && tokenPublicKey !== publicKey?.toBase58()) {
          console.warn(
            "Token wallet address mismatch. Expected:",
            publicKey?.toBase58(),
            "Got:",
            tokenPublicKey
          );
          // Clear the old token but don't disconnect the wallet
          localStorage.removeItem(PUFFY_TOKEN_KEY);
          delete axiosInstance.defaults.headers.common["Authorization"];
          // Keep the wallet connected, just set status to connected (not authenticated)
          setAuthStatus("connected");
          return;
        }
        axiosInstance.defaults.headers.common["Authorization"] =
          `Bearer ${token}`;
        setAuthStatus("authenticated");
      }
    }, 300);

    // Clean up the timer if the component unmounts or publicKey changes
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [publicKey]);

  useEffect(() => {
    if (disconnecting) {
      logout();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [disconnecting]);

  const logout = () => {
    disconnect();
    localStorage.removeItem(PUFFY_TOKEN_KEY);
    delete axiosInstance.defaults.headers.common["Authorization"];
    setAuthStatus("disconnected");
  };

  return (
    <WalletLoginContext.Provider
      value={{
        logout,
        signin,
        login,
        status: authStatus,
        eligibleVerificationStatus: verifyEligible.status,
        eligibleVerificationError: verifyEligible.error,
        resetEligibleVerification: verifyEligible.reset,
        signinStatus: signinMutation.status,
        signinError: signinMutation.error,
        resetSignin: signinMutation.reset,
      }}
    >
      {children}
    </WalletLoginContext.Provider>
  );
};

const parseTokenToPublicKey = (token: string) => {
  try {
    // Split JWT to get payload part (second part)
    const base64Url = token.split(".")[1];
    // Convert base64url to standard base64
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    // Decode and parse JSON
    const payload = JSON.parse(Buffer.from(base64, "base64").toString());
    return payload.wallet_address;
  } catch (error) {
    console.error("JWT decode failed:", error);
    return null;
  }
};
