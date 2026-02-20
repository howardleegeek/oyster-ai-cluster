import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'getpuffy.ai',
      },
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
    formats: ["image/avif", "image/webp"],
  },
  async headers() {
    // if (isDev) {
    //   return [
    //     {
    //       source: '/:path*\\.(jpg|jpeg|png|gif|webp|svg|mp4|webm)',
    //       headers: [
    //         {
    //           key: 'Cache-Control',
    //           value: 'no-cache, no-store, must-revalidate',
    //         },
    //       ],
    //     },
    //   ];
    // }

    return [
      {
        source: '/:path*\\.(jpg|jpeg|png|gif|webp|svg)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=2592000, immutable',
          },
        ],
      },
      {
        source: '/:path*\\.(mp4|webm|ogg)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=604800',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
