const path = require("path");

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: { externalDir: true },
  webpack: (config) => {
    config.resolve.alias["@aero/ui"] = path.resolve(__dirname, "../packages/ui");
    return config;
  },
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
  },
};

module.exports = nextConfig;
