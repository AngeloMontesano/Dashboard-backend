export function getBaseURL(): string {
  const envUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;
  return envUrl && envUrl.length > 0 ? envUrl : 'http://localhost:3000';
}
