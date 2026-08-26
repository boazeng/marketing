/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL of the lead proxy. Public by design -- see src/lib/leads.ts. */
  readonly VITE_LEAD_ENDPOINT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
