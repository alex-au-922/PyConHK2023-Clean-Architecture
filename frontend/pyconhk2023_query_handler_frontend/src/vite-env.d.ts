/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_GATEWAY_DOMAIN: string
    readonly VITE_ECS_CLUSTER_ALB: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}