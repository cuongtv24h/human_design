"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ClientForm } from "@/components/ClientForm";
import { Card, PageHeader } from "@/components/ui";
import { api } from "@/lib/api";
import type { Client } from "@/lib/types";

export default function NewClientPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  return (
    <>
      <PageHeader title="Thêm khách hàng" description="Thông tin sinh dùng để tính BodyGraph. Giờ sinh nhập theo giờ Việt Nam." />
      <Card className="max-w-3xl p-6">
        <ClientForm requireConsent submitLabel="Lưu khách hàng" onCancel={() => router.back()}
          onSubmit={async (value) => {
            const client = await api.post<Client>("/clients", value);
            await queryClient.invalidateQueries({ queryKey: ["clients"] });
            queryClient.invalidateQueries({ queryKey: ["dashboard"] });
            router.push(`/clients/${client.id}?created=1`);
          }} />
      </Card>
    </>
  );
}
