/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_LAMBDA_API_GATEWAY_DOMAIN: string;
  readonly VITE_ECS_API_GATEWAY_DOMAIN: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}