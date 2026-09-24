// pm2 process file for the VPS (no Docker, no CI — plan §10).
//   pm2 start deploy/ecosystem.config.cjs && pm2 save
// Python services read /srv/human_design/.env themselves (backend/api/settings.py),
// so this file does not depend on pm2's env_file support.
const ROOT = process.env.HD_ROOT || "/srv/human_design";

module.exports = {
  apps: [
    {
      name: "hd-api",
      cwd: ROOT,
      script: ".venv/bin/uvicorn",
      args: "backend.api.main:app --host 127.0.0.1 --port 8001 --workers 2 --proxy-headers",
      interpreter: "none",
      max_memory_restart: "600M",
      env: { HD_ENV: "production" },
    },
    // No separate worker/Redis (owner decision, option a): LLM-mode reports run as background
    // tasks inside hd-api with a heartbeat; after a restart each worker resumes interrupted
    // reports automatically (backend/api/jobs.py).
    {
      name: "hd-web",
      cwd: `${ROOT}/web`,
      script: "node_modules/.bin/next",
      args: "start -H 127.0.0.1 -p 3000",
      interpreter: "none",
      max_memory_restart: "500M",
      env: { NODE_ENV: "production", API_INTERNAL_URL: "http://127.0.0.1:8001" },
    },
    {
      // Optional: existing REST bridge for ChatGPT Custom GPT Actions.
      name: "hd-gpt-bridge",
      cwd: `${ROOT}/mcp`,
      script: "../.venv/bin/uvicorn",
      args: "openapi_server:app --host 127.0.0.1 --port 8000",
      interpreter: "none",
      autorestart: true,
    },
  ],
};
