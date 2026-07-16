import { useAuth } from "@clerk/nextjs";
import { useCallback } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function useApi() {
  const { getToken } = useAuth();

  const request = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const token = await getToken();
    const headers = new Headers(options.headers);
    
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
    
    // Do not set Content-Type if sending FormData (browser handles multipart boundaries)
    if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `API request failed: ${response.statusText}`);
    }

    return response.json();
  }, [getToken]);

  return { request };
}
