"use client";

import { Input, ConfigProvider, message, Button } from "antd";
import { useState, useEffect } from "react";
import {
  useUpdateUserEmailUserEmailPost,
  useGetUserInfoUserInfoGet,
} from "@/types";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CloseCircleFilled, CheckCircleFilled } from "@ant-design/icons";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useQueryClient } from "@tanstack/react-query";
import { getGetUserInfoUserInfoGetQueryKey } from "@/types";
import { fluidSize } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import {
  sendEmailVerificationCode,
  verifyEmailCode,
} from "@/lib/emailVerification";

export default function MyEmailPage() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [api, contextHolder] = message.useMessage();
  const { mutateAsync: updateEmail, isPending } =
    useUpdateUserEmailUserEmailPost();
  const { status } = useWalletLogin();
  const queryClient = useQueryClient();
  const { data: userInfo, isLoading: isLoadingUserInfo } =
    useGetUserInfoUserInfoGet({
      query: {
        enabled: status === "authenticated",
      },
    });

  const {
    mutateAsync: sendCode,
    isPending: isSendingCode,
  } = useMutation({
    mutationFn: (targetEmail: string) =>
      sendEmailVerificationCode({ email: targetEmail }),
    onSuccess: () => {
      setCode("");
      setCodeSent(true);
      api.success({
        content: "Verification code sent. Please check your inbox.",
        ...NOTIFICATION_CONFIG,
        icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
      });
    },
    onError: (error: any) => {
      api.error({
        content:
          error?.response?.data?.detail ||
          error?.message ||
          "Failed to send verification code. Please try again.",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    },
  });

  const {
    mutateAsync: verifyAndUpdate,
    isPending: isVerifying,
  } = useMutation({
    mutationFn: async (payload: { email: string; code: string }) => {
      const res = await verifyEmailCode(payload);
      if (!res.success) {
        throw new Error(res.message || "Invalid verification code.");
      }
      return updateEmail({ data: { email: payload.email } });
    },
  });

  // Set initial email value if user already has one
  useEffect(() => {
    if (userInfo?.email) {
      setEmail(userInfo.email);
    } else if (!isLoadingUserInfo && userInfo && !userInfo.email) {
      // User info loaded but no email - clear the field
      setEmail("");
    }
  }, [userInfo?.email, isLoadingUserInfo, userInfo]);

  const handleChange = () => {
    if (!isEditing) {
      setIsEditing(true);
      setCode("");
      setCodeSent(false);
    }
  };

  const handleSendCode = async () => {
    if (!email.trim()) return;
    await sendCode(email.trim());
  };

  const handleSubmit = async () => {
    if (!email.trim() || !code.trim()) {
      return;
    }

    try {
      await verifyAndUpdate({ email: email.trim(), code: code.trim() });

      // Refetch user info to get updated email
      queryClient.invalidateQueries({
        queryKey: getGetUserInfoUserInfoGetQueryKey(),
      });

      setIsEditing(false);
      setCode("");
      setCodeSent(false);
      api.success({
        content: "Email verified and updated successfully!",
        ...NOTIFICATION_CONFIG,
        icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
      });
    } catch (error: any) {
      api.error({
        content:
          error?.response?.data?.detail ||
          error?.message ||
          "Verification failed. Please check the code and try again.",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  };

  const handleCancel = () => {
    if (userInfo?.email) {
      setEmail(userInfo.email);
    }
    setIsEditing(false);
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      {contextHolder}
      <div className="flex flex-col max-w-[600px] w-full px-[12px]">
        <div
          className="text-[#17191A] font-semibold font-pingfang mb-6 md:mb-10"
          style={{ fontSize: fluidSize(20, 24) }}
        >
          My Contact Email
        </div>

        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-6">
            <div className="flex flex-row gap-3 items-center">
              <ConfigProvider
                theme={{
                  components: {
                    Input: {
                      colorPrimary: "black",
                      colorPrimaryHover: "transparent",
                      activeBorderColor: "transparent",
                      hoverBorderColor: "transparent",
                      colorBorder: "rgba(0, 0, 0, 0.10)",
                      activeShadow: "0 0 0 0px transparent",
                      boxShadow: "none",
                      paddingInline: 14,
                      paddingBlock: 8,
                      borderRadius: 9999,
                      fontSize: 16,
                      fontFamily: "PingFang SC, system-ui, sans-serif",
                      colorText: "rgba(0, 0, 0, 0.90)",
                      colorTextPlaceholder: "#00000080",
                      colorTextDisabled: "#00000080",
                    },
                    Button: {
                      colorPrimary: "black",
                      colorPrimaryHover: "black",
                      primaryColor: "white",
                    },
                  },
                }}
              >
                <Input
                  type="email"
                  placeholder={
                    isLoadingUserInfo ? "Loading..." : "Email Address"
                  }
                  value={isLoadingUserInfo ? "Loading..." : email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={!isEditing || isLoadingUserInfo}
                  className="flex-1 rounded-full [&.ant-input-disabled]:opacity-100"
                  style={{
                    background: isEditing ? "white" : "transparent",
                    caretColor: "black",
                  }}
                  onPressEnter={() => {
                    if (!codeSent) {
                      handleSendCode();
                    } else {
                      handleSubmit();
                    }
                  }}
                />
              </ConfigProvider>
              {!isEditing && (
                <Button
                  onClick={handleChange}
                  disabled={isLoadingUserInfo}
                  className="rounded-full md:min-w-[160px] min-w-[120px]"
                  style={{
                    paddingInline: 14,
                    paddingBlock: 8,
                    height: "auto",
                    borderColor: "rgba(0, 0, 0, 0.10)",
                    color: "#1A1A1A",
                    background: "#F1F1F1",
                  }}
                >
                  Change
                </Button>
              )}
            </div>
            {isEditing && (
              <div className="flex flex-col gap-3">
                <div className="flex flex-row gap-3 items-center">
                  <Input
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Enter verification code"
                    disabled={!codeSent || isVerifying}
                    maxLength={6}
                    className="flex-1 rounded-full"
                  />
                  <Button
                    onClick={handleSendCode}
                    disabled={!email.trim() || isSendingCode}
                    loading={isSendingCode}
                    className="rounded-full md:min-w-[140px] min-w-[110px]"
                    style={{
                      paddingInline: 14,
                      paddingBlock: 8,
                      height: "auto",
                      borderColor: "rgba(0, 0, 0, 0.10)",
                      color: "#1A1A1A",
                      background: "#F1F1F1",
                    }}
                  >
                    {codeSent ? "Resend code" : "Send code"}
                  </Button>
                </div>
                <div className="flex flex-row gap-4 items-start">
                  <Button
                    onClick={handleCancel}
                    disabled={isPending || isSendingCode || isVerifying}
                    className="rounded-full md:min-w=[160px] min-w-[120px]"
                    style={{
                      paddingInline: 14,
                      paddingBlock: 8,
                      height: "auto",
                      borderColor: "rgba(0, 0, 0, 0.10)",
                      color: "rgba(0, 0, 0, 0.90)",
                      background: "transparent",
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="primary"
                    onClick={handleSubmit}
                    disabled={
                      !email.trim() || !code.trim() || isPending || isVerifying
                    }
                    loading={isVerifying || isPending}
                    className="rounded-full md:min-w-[160px] min-w-[120px]"
                    style={{
                      paddingInline: 14,
                      paddingBlock: 8,
                      height: "auto",
                      background: "black",
                      borderColor: "black",
                      color: "white",
                    }}
                  >
                    Verify & Save
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
