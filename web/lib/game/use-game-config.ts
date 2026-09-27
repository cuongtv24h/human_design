"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { registerCustomOptions } from "./engine";
import { customBankMap, type GameServerConfig } from "./runtime";

const TTL = 5 * 60 * 1000;
let cache: { at: number; config: GameServerConfig } | null = null;

/** Config Game Manager dùng chung toàn client (cache 5 phút, lỗi thì null = dùng TS). */
export function useGameConfig(): { config: GameServerConfig | null; ready: boolean } {
  const [state, setState] = useState<{ config: GameServerConfig | null; ready:boolean}>(
    () =>
      cache && Date.now() - cache.at < TTL
        ? { config: cache.config, ready: true }
        : { config: null, ready: false },
  );
  useEffect(() => {
    let live = true;
    if (cache && Date.now() - cache.at < TTL) {
      registerCustomOptions(customBankMap(cache.config));
      setState({ config: cache.config, ready: true });
      return;
    }
    api
      .get<GameServerConfig>("/public/game/config")
      .then((config) => {
        if (!live) return;
        cache = { at: Date.now(), config };
        registerCustomOptions(customBankMap(config));
        setState({ config, ready: true });
      })
      .catch(() => {
        if (live) setState({ config: null, ready: true });
      });
    return () => {
      live = false;
    };
  }, []);
  return state;
}
