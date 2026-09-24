"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import type { User } from "./types";

export function useMe() {
  return useQuery({ queryKey: ["me"], queryFn: () => api.get<User>("/auth/me"), staleTime: 60_000 });
}
