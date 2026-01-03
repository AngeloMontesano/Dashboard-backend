// src/api/platform.ts
import axios from "axios";
import { getBaseURL } from "./base";

/*
  Platform API
  - Endpunkte ohne Admin Key
*/

const http = axios.create({
  baseURL: getBaseURL(),
  timeout: 15000,
});

export async function platformHealth(): Promise<boolean> {
  await http.get("/health");
  return true;
}

export async function platformHealthDb(): Promise<boolean> {
  await http.get("/health/db");
  return true;
}
