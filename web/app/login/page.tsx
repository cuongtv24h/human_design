"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { Logo } from "@/components/Logo";
import { Button, Card, ErrorBox, Field, Input } from "@/components/ui";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const user = await api.post<User>("/auth/login", { email, password });
      queryClient.setQueryData(["me"], user);
      const next = params.get("next");
      router.replace(next && next.startsWith("/") && !next.startsWith("//") ? next : "/");
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-sm p-7">
      <form onSubmit={onSubmit} className="space-y-4">
        <Field label="Email" htmlFor="email">
          <Input id="email" type="email" autoComplete="username" required autoFocus value={email}
            onChange={(e) => setEmail(e.target.value)} placeholder="ban@vidu.com" />
        </Field>
        <Field label="Mật khẩu" htmlFor="password">
          <Input id="password" type="password" autoComplete="current-password" required value={password}
            onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <ErrorBox error={error} />
        <Button type="submit" className="w-full" loading={loading}>Đăng nhập</Button>
      </form>
    </Card>
  );
}

export default function LoginPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="flex flex-col items-center gap-3 text-center">
        <Logo className="size-12" />
        <div>
          <h1 className="text-xl font-bold text-ink">Human Design Studio</h1>
          <p className="text-sm text-muted">Khu vực quản trị dành cho chuyên viên tư vấn</p>
        </div>
      </div>
      <Suspense>
        <LoginForm />
      </Suspense>
      <p className="max-w-sm text-center text-xs text-muted">
        Tài khoản do quản trị viên cấp. Quên mật khẩu? Liên hệ quản trị viên để được đặt lại.
      </p>
    </main>
  );
}
