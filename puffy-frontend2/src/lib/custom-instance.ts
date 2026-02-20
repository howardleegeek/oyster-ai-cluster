import axios, { AxiosRequestConfig } from "axios";
import { config } from "./axios";

export const axiosInstance = axios.create(config);

// Add interceptor to log response
axiosInstance.interceptors.response.use(
  (response) => {
    // Log the request URL and params for debugging
    // console.log(response);
    // console.log({
    //   url: response.config.url,
    //   headers: response.config.headers,
    //   params: response.config.params,
    //   data: response.data,
    //   status: response.status,
    // });
    return response;
  },
  (error) => {
    // Skip logging if error is due to missing token
    if (error.message === "No token provided for protected route") {
      return Promise.reject(error);
    }

    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export function customInstance<T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig
): Promise<T> {
  const source = axios.CancelToken.source();
  const promise = axiosInstance({
    ...config,
    ...options,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-expect-error - cancel is not defined in the type
  promise.cancel = () => {
    source.cancel("Query was cancelled");
  };

  return promise;
}

export default customInstance;
