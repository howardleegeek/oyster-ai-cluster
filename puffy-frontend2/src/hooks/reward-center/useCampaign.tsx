"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  buildNftMintingTransaction,
  buildConnection,
  sendAndConfirmTransaction,
} from "@/lib/transaction";
import {
  Campaign,
  checkEligibleCampaignsCampaignCheckEligibleGet,
  getGetUserCampaignInfoCampaignsCampaignInfoGetQueryKey,
  useGetCampaignCampaignsCampaignGet,
  useGetUserCampaignInfoCampaignsCampaignInfoGet,
  User,
  promoteCompleteCampaignsCampaignPromotionPromotionIdPromoteCompleteGet,
  checkUserCampaignAlreadyPaidCampaignsCampaignPromotionPromotionIdAlreadyPaidGet,
  promoteMintGasCampaignsCampaignPromotionPromotionIdPromoteMintGasPost,
} from "@/types";
import { useWalletLogin } from "../common/useWalletLogin";
import { LAMPORTS_PER_SOL } from "@solana/web3.js";

export enum CampaignStatus {
  UNCHECKED = -1,
  ERROR = 0,
  LOADING = 1,
  UNELIGIBLE = 2,
  UNCOMPLETED = 3,
  UNCLAIMED = 4,
  CLAIMING = 5,
  CLAIMED = 6,
}

interface CampaignContextType {
  campaignInfo: Campaign | undefined;
  userInfo: User | undefined;
  refetchUserInfo: () => void;
  status: CampaignStatus;
  setStatus: (status: CampaignStatus) => void;
  mint: (
    onStart?: () => void,
    onSuccess?: () => void,
    onError?: (error: Error) => void
  ) => Promise<void>;
  mintStatus: "idle" | "loading" | "error" | "success";
  isEligible: boolean;
  promotionId: number | undefined;
}

const CampaignContext = createContext<CampaignContextType>({
  campaignInfo: undefined,
  userInfo: undefined,
  refetchUserInfo: async () => {},
  status: CampaignStatus.LOADING,
  setStatus: () => {},
  mint: async () => {},
  mintStatus: "idle",
  isEligible: false,
  promotionId: undefined,
});

export const useCampaign = () => {
  const context = useContext(CampaignContext);
  if (!context) {
    throw new Error("useCampaign must be used within CampaignProvider");
  }
  return context;
};

export const REFERRAL_CODE_KEY = "referral_code";
export const MINTING_CODE_KEY = "minting_code";

export const CampaignProvider = ({
  children,
  campaignName,
  promotionId,
}: {
  children: React.ReactNode;
  campaignName: string;
  promotionId?: number;
}) => {
  const [status, setStatus] = useState<CampaignStatus>(
    CampaignStatus.UNCHECKED
  );
  const wallet = useWallet();
  const { publicKey } = useWallet();
  const { status: authStatus } = useWalletLogin();
  const { data: campaignInfo } = useGetCampaignCampaignsCampaignGet(
    campaignName,
    {
      query: {
        enabled: !!campaignName,
      },
    }
  );
  const queryClient = useQueryClient();
  const { data: userInfo, refetch: refetchUserInfo } =
    useGetUserCampaignInfoCampaignsCampaignInfoGet(campaignName, {
      query: {
        enabled: authStatus === "authenticated",
      },
    });

  const updateStatusBasedOnUserInfo = useCallback(
    async (userInfo: User | undefined) => {
      if (!userInfo) {
        setStatus(CampaignStatus.LOADING);
        return;
      }
      if (!publicKey) {
        setStatus(CampaignStatus.UNELIGIBLE);
        console.log("can not detect solana wallet");
        return;
      }
      const isEligible = userInfo.eligibles?.find(
        (eligible) => eligible.campaign_id === campaignInfo?.campaign_id
      )?.is_eligible;
      if (isEligible === undefined) {
        console.log("the user has not been checked eligibility");
        setStatus(CampaignStatus.UNELIGIBLE);

        // check if the user is eligible
        await checkEligibleCampaignsCampaignCheckEligibleGet(campaignName);
        // refetch the user info
        queryClient.invalidateQueries({
          queryKey:
            getGetUserCampaignInfoCampaignsCampaignInfoGetQueryKey(
              campaignName
            ),
        });
        return;
      }

      if (isEligible === false) {
        console.log("the user is not eligible");
        setStatus(CampaignStatus.UNELIGIBLE);
        return;
      }

      const nft = userInfo.nfts?.find(
        (nft) =>
          nft.campaign_id === campaignInfo?.campaign_id &&
          nft.promotion_id === promotionId
      );

      console.log("nft", nft);
      console.log("promotionId", promotionId);

      if (!nft) {
        setStatus(CampaignStatus.LOADING);
        // call promote complete to generate a nft metadata
        if (!promotionId) {
          console.error("promotionId is required but not provided");
          setStatus(CampaignStatus.UNELIGIBLE);
          return;
        }
        try {
          await promoteCompleteCampaignsCampaignPromotionPromotionIdPromoteCompleteGet(
            campaignName,
            promotionId
          );
        } catch (error) {
          console.error("Error promoting complete:", error);
          setStatus(CampaignStatus.UNELIGIBLE);
          return;
        }
        // refecth user info
        refetchUserInfo();
        return;
      }

      if (nft?.status === "new") {
        setStatus(CampaignStatus.UNCLAIMED);
      } else if (
        ["minted", "mint_failed", "payment_confirmed", "paid"].includes(
          nft?.status ?? ""
        )
      ) {
        setStatus(CampaignStatus.CLAIMED);
      }
    },
    [
      campaignInfo?.campaign_id,
      campaignName,
      publicKey,
      queryClient,
      refetchUserInfo,
      promotionId,
    ]
  );

  useEffect(() => {
    updateStatusBasedOnUserInfo(userInfo);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userInfo]);

  // Listen to authStatus changes and handle login/logout events
  useEffect(() => {
    if (authStatus === "authenticated") {
      // Handle login success - invalidate queries to refetch user info
      queryClient.invalidateQueries({
        queryKey:
          getGetUserCampaignInfoCampaignsCampaignInfoGetQueryKey(campaignName),
      });
    } else if (authStatus === "disconnected") {
      // Handle logout - reset status and clear queries
      setStatus(CampaignStatus.UNELIGIBLE);
      queryClient.removeQueries({
        predicate: (query) => {
          return query.state.fetchStatus === 'idle';
        },
      });
    }
  }, [authStatus, campaignName, queryClient]);

  // Mint mutation
  const { mutateAsync: mintMutate, status: mintStatus } = useMutation({
    mutationFn: async (params: {
      onStart?: () => void;
      onSuccess?: () => void;
      onError?: (error: Error) => void;
    }) => {
      const { onStart } = params;
      if (!publicKey) {
        throw new Error("wallet not connected");
      }

      if (!promotionId) {
        throw new Error("promotionId is required");
      }

      setStatus(CampaignStatus.CLAIMING);

      if (status > CampaignStatus.CLAIMING) {
        throw new Error("you have already claimed");
      }

      const paided =
        await checkUserCampaignAlreadyPaidCampaignsCampaignPromotionPromotionIdAlreadyPaidGet(
          campaignName,
          promotionId,
          {
            // put timestamp of utc now in seconds
            after: Math.floor(Date.now() / 1000),
          }
        );
      if (paided.already_paid === true) {
        setStatus(CampaignStatus.CLAIMING);
        refetchUserInfo();
        return;
      }
      // wait for 3 second
      await new Promise((resolve) => setTimeout(resolve, 3000));

      if (onStart) onStart();
      const data =
        await promoteCompleteCampaignsCampaignPromotionPromotionIdPromoteCompleteGet(
          campaignName,
          promotionId
        );

      if (!data) {
        throw new Error(
          "failed to get the minting data, please try again later"
        );
      }
      if (!publicKey) {
        throw new Error("wallet not connected");
      }
      if (!userInfo) {
        throw new Error(
          "failed to find your account, please disconnect and reconnect your wallet"
        );
      }

      // build minting transaction
      const transaction = await buildNftMintingTransaction(
        publicKey,
        data.nft_id,
        userInfo.user_id,
        data.gas_fee
      );

      // check if the user has enough balance
      const connection = buildConnection();
      const balance = await connection.getBalance(publicKey);
      if (balance < (data.gas_fee + 0.001) * LAMPORTS_PER_SOL) {
        throw new Error(
          `insufficient balance, please make sure you have at least ${
            data.gas_fee + 0.001
          } SOL in your wallet`
        );
      }

      let signature = "";
      try {
        signature = await sendAndConfirmTransaction(
          transaction,
          async (transaction) =>
            wallet?.sendTransaction(transaction, buildConnection()),
          async (signature) => {
            const latestBlockhash =
              await buildConnection().getLatestBlockhash();
            await buildConnection().confirmTransaction({
              signature,
              blockhash: transaction.recentBlockhash!,
              lastValidBlockHeight: latestBlockhash.lastValidBlockHeight,
            });
          }
        );
      } catch (error) {
        throw error;
      }
      try {
        // send the signature to the server
        await promoteMintGasCampaignsCampaignPromotionPromotionIdPromoteMintGasPost(
          campaignName,
          promotionId,
          {
            transaction_hash: signature,
            nft_id: data.nft_id,
          }
        );
      } catch (error) {
        console.error("Error sending the signature to the server:", error);
        throw new Error("fail to send the signature to the server");
      }

      refetchUserInfo();
      return;
    },
    onSuccess: async (data, params) => {
      if (params.onSuccess) params.onSuccess();
      setStatus(CampaignStatus.CLAIMING);
    },
    onError: (error, params) => {
      if (params.onError) params.onError(error);
      console.log("mint error", error);
      setStatus(CampaignStatus.UNCLAIMED);
    },
  });

  // update nft status by polling
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (status === CampaignStatus.CLAIMING) {
      interval = setInterval(() => {
        queryClient.invalidateQueries({
          queryKey:
            getGetUserCampaignInfoCampaignsCampaignInfoGetQueryKey(
              campaignName
            ),
        });
      }, 5000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [status, campaignName, queryClient]);

  // Map status values to the expected format
  const mapStatus = (
    status: string
  ): "idle" | "loading" | "error" | "success" => {
    if (status === "pending") return "loading";
    return status as "idle" | "loading" | "error" | "success";
  };

  const mint = async (
    onStart?: () => void,
    onSuccess?: () => void,
    onError?: (error: Error) => void
  ) => {
    await mintMutate({ onStart, onSuccess, onError });
  };

  return (
    <CampaignContext.Provider
      value={{
        campaignInfo: campaignInfo,
        userInfo,
        refetchUserInfo,
        status,
        setStatus,
        mint,
        mintStatus: mapStatus(mintStatus),
        isEligible: status > CampaignStatus.UNELIGIBLE,
        promotionId,
      }}
    >
      {children}
    </CampaignContext.Provider>
  );
};
