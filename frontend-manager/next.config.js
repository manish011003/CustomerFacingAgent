/** @type {import('next').NextConfig} */
const exporting = process.env.EXPORT === "1";
const onVercel = Boolean(process.env.VERCEL);
const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const nested = exporting || onVercel;

const nextConfig = {
  reactStrictMode: true,
  ...(nested ? { basePath: "/ops" } : {}),
  ...(exporting
    ? {
        output: "export",
        trailingSlash: true,
        images: { unoptimized: true },
      }
    : onVercel
      ? {}
      : {
          async rewrites() {
            return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
          },
        }),
};

module.exports = nextConfig;
