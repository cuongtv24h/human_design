"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UserPlus } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Badge, Button, Card, ErrorBox, Field, Input, Modal, PageHeader, Spinner, cx } from "@/components/ui";
import { api } from "@/lib/api";
import { useMe } from "@/lib/auth";
import { formatTimestamp } from "@/lib/format";
import type { Role, User } from "@/lib/types";

function NewUserForm({ onDone }: { onDone: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role: "coach" as Role });
  const create = useMutation({
    mutationFn: () => api.post<User>("/users", form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      onDone();
    },
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    create.mutate();
  };
  return (
    <form onSubmit={submit} className="grid gap-4 p-5 sm:grid-cols-2">
      <Field label="Họ tên" htmlFor="u-name"><Input id="u-name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></Field>
      <Field label="Email đăng nhập" required htmlFor="u-email"><Input id="u-email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
      <Field label="Mật khẩu tạm" required htmlFor="u-pass" hint="Tối thiểu 8 ký tự. Gửi riêng cho người dùng.">
        <Input id="u-pass" type="text" minLength={8} required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
      </Field>
      <Field label="Vai trò" htmlFor="u-role">
        <select id="u-role" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as Role })}
          className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm">
          <option value="coach">Chuyên viên tư vấn — chỉ thấy khách hàng của mình</option>
          <option value="admin">Quản trị viên — thấy toàn bộ và quản lý tài khoản</option>
        </select>
      </Field>
      <div className="sm:col-span-2">
        <ErrorBox error={create.error} className="mb-3" />
        <div className="flex gap-2">
          <Button type="submit" loading={create.isPending}>Tạo tài khoản</Button>
          <Button type="button" variant="secondary" onClick={onDone}>Hủy</Button>
        </div>
      </div>
    </form>
  );
}

function EditUserModal({ user, isSelf, onClose }: { user: User; isSelf: boolean; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ full_name: user.full_name, role: user.role });
  const save = useMutation({
    mutationFn: () => api.patch<User>(`/users/${user.id}`, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      onClose();
    },
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    save.mutate();
  };
  return (
    <Modal title="Sửa tài khoản" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-muted">{user.email} · Tạo {formatTimestamp(user.created_at)}</p>
        <Field label="Họ tên" htmlFor="e-name">
          <Input id="e-name" value={form.full_name} maxLength={200}
            onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </Field>
        <Field label="Vai trò" htmlFor="e-role" hint={isSelf ? "Không thể tự đổi vai trò của chính mình." : undefined}>
          <select id="e-role" value={form.role} disabled={isSelf}
            onChange={(e) => setForm({ ...form, role: e.target.value as Role })}
            className="block w-full rounded-lg border border-line bg-white px-3 py-2 text-sm disabled:bg-paper">
            <option value="coach">Chuyên viên tư vấn — chỉ thấy khách hàng của mình</option>
            <option value="admin">Quản trị viên — thấy toàn bộ và quản lý tài khoản</option>
          </select>
        </Field>
        <ErrorBox error={save.error} />
        <div className="flex gap-2">
          <Button type="submit" loading={save.isPending}>Lưu</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </form>
    </Modal>
  );
}

function ResetPasswordModal({ user, onClose }: { user: User; onClose: () => void }) {
  const queryClient = useQueryClient();
  const [password, setPassword] = useState("");
  const reset = useMutation({
    mutationFn: () => api.patch<User>(`/users/${user.id}`, { password }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      onClose();
    },
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    reset.mutate();
  };
  return (
    <Modal title="Đặt lại mật khẩu" onClose={onClose}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-muted">
          Tài khoản <strong className="text-ink">{user.full_name || user.email}</strong> sẽ dùng mật khẩu mới
          ở lần đăng nhập tiếp theo. Các phiên đang đăng nhập của người này sẽ bị đăng xuất.
        </p>
        <Field label="Mật khẩu tạm mới" required htmlFor="r-pass" hint="Tối thiểu 8 ký tự. Gửi riêng cho người dùng.">
          <Input id="r-pass" type="text" minLength={8} required value={password}
            onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <ErrorBox error={reset.error} />
        <div className="flex gap-2">
          <Button type="submit" loading={reset.isPending}>Đặt lại</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </form>
    </Modal>
  );
}

function DeleteUserModal({ user, onClose }: { user: User; onClose: () => void }) {
  const queryClient = useQueryClient();
  const remove = useMutation({
    mutationFn: () => api.del(`/users/${user.id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      onClose();
    },
  });
  return (
    <Modal title="Xóa tài khoản" onClose={onClose}>
      <div className="space-y-4">
        <p className="text-sm text-muted">
          Xóa hẳn tài khoản <strong className="text-ink">{user.full_name || user.email}</strong>?
          Chỉ xóa được tài khoản chưa có khách hàng/báo cáo — nếu còn dữ liệu, hãy dùng Khóa tài khoản.
        </p>
        <ErrorBox error={remove.error} />
        <div className="flex gap-2">
          <Button variant="danger" loading={remove.isPending} onClick={() => remove.mutate()}>Xóa hẳn</Button>
          <Button variant="secondary" onClick={onClose}>Hủy</Button>
        </div>
      </div>
    </Modal>
  );
}

export default function UsersPage() {
  const me = useMe();
  const queryClient = useQueryClient();
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [resetting, setResetting] = useState<User | null>(null);
  const [deleting, setDeleting] = useState<User | null>(null);
  const users = useQuery({ queryKey: ["users"], queryFn: () => api.get<User[]>("/users"), enabled: me.data?.role === "admin" });
  const toggle = useMutation({
    mutationFn: (u: User) => api.patch<User>(`/users/${u.id}`, { is_active: !u.is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (me.data && me.data.role !== "admin") return <ErrorBox error="Chỉ quản trị viên được truy cập trang này." />;

  return (
    <>
      <PageHeader title="Tài khoản" description="Cấp tài khoản cho chuyên viên tư vấn trong tổ chức."
        actions={!adding && <Button onClick={() => setAdding(true)}><UserPlus className="size-4" /> Thêm tài khoản</Button>} />
      {adding && <Card className="mb-6"><NewUserForm onDone={() => setAdding(false)} /></Card>}
      <ErrorBox error={users.error ?? toggle.error} className="mb-4" />
      <Card>
        {users.isLoading || !users.data ? <Spinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-4 py-3 font-medium">Người dùng</th>
                  <th className="px-4 py-3 font-medium">Vai trò</th>
                  <th className="px-4 py-3 font-medium">Trạng thái</th>
                  <th className="px-4 py-3 font-medium">Đăng nhập cuối</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {users.data.map((u) => {
                  const isSelf = u.id === me.data?.id;
                  return (
                    <tr key={u.id} className={cx("border-b border-line/70 last:border-0", !u.is_active && "opacity-60")}>
                      <td className="px-4 py-3">
                        <div className="font-medium text-ink">{u.full_name || "—"}</div>
                        <div className="text-xs text-muted">{u.email}</div>
                      </td>
                      <td className="px-4 py-3"><Badge tone={u.role === "admin" ? "gold" : "brand"}>{u.role === "admin" ? "Quản trị viên" : "Chuyên viên"}</Badge></td>
                      <td className="px-4 py-3">{u.is_active ? "Đang hoạt động" : "Đã khóa"}</td>
                      <td className="px-4 py-3 text-muted">{u.last_login_at ? formatTimestamp(u.last_login_at) : "Chưa từng"}</td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap justify-end gap-1.5">
                          <Button variant="secondary" className="px-3 py-1 text-xs" onClick={() => setEditing(u)}>Sửa</Button>
                          {!isSelf && (
                            <>
                              <Button variant="secondary" className="px-3 py-1 text-xs" onClick={() => setResetting(u)}>Đặt lại MK</Button>
                              <Button variant={u.is_active ? "danger" : "secondary"} className="px-3 py-1 text-xs"
                                loading={toggle.isPending && toggle.variables?.id === u.id} onClick={() => toggle.mutate(u)}>
                                {u.is_active ? "Khóa" : "Mở khóa"}
                              </Button>
                              <Button variant="danger" className="px-3 py-1 text-xs" onClick={() => setDeleting(u)}>Xóa</Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
      {editing && <EditUserModal user={editing} isSelf={editing.id === me.data?.id} onClose={() => setEditing(null)} />}
      {resetting && <ResetPasswordModal user={resetting} onClose={() => setResetting(null)} />}
      {deleting && <DeleteUserModal user={deleting} onClose={() => setDeleting(null)} />}
    </>
  );
}
