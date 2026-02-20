import { axiosInstance } from "@/lib/custom-instance";

export interface SendEmailCodeRequest {
  email: string;
}

export interface VerifyEmailCodeRequest {
  email: string;
  code: string;
}

export interface EmailCodeResponse {
  success: boolean;
  message?: string;
}

// Assumes backend exposes these endpoints:
// POST /user/email/send-code  { email }
// POST /user/email/verify-code { email, code }

export async function sendEmailVerificationCode(
  payload: SendEmailCodeRequest,
): Promise<EmailCodeResponse> {
  const res = await axiosInstance.post<EmailCodeResponse>(
    "/user/email/send-code",
    payload,
  );
  return res.data;
}

export async function verifyEmailCode(
  payload: VerifyEmailCodeRequest,
): Promise<EmailCodeResponse> {
  const res = await axiosInstance.post<EmailCodeResponse>(
    "/user/email/verify-code",
    payload,
  );
  return res.data;
}

