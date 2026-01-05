// src/api/platform.ts
import { api } from "./client";

/*
  Platform API
  - Endpunkte ohne Admin Key
*/

export async function platformHealth(): Promise<boolean> {
  await api.get("/health");
  return true;
}

export async function platformHealthDb(): Promise<boolean> {
  await api.get("/health/db");
  return true;
}
