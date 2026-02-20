import axios from "axios";

const PUFFY_TOKEN_KEY = "puffy_token_campaign";

export const config = {
  baseURL: process.env.NEXT_PUBLIC_BACKEND_BASE_URL,
  timeout: 15_000,
};

// function to create a new client with same config
export const createClient = (baseURL?: string, token?: string) => {
  const newClient = axios.create({
    ...config,
    baseURL: baseURL || config.baseURL,
  });

  newClient.interceptors.request.use((config) => {
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  newClient.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      if (error.response?.status === 401) {
        if (typeof window !== "undefined") {
          localStorage.removeItem(PUFFY_TOKEN_KEY);
        }
      }
      return Promise.reject(error);
    }
  );

  return newClient;
};
