/** @type {import('next').NextConfig} */
const exporting = process.env.EXPORT === "1";
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig = {
  reactStrictMode: true,
  ...(exporting
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : {
        async rewrites() {
          return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
        },
      }),
};

module.exports = nextConfig;
