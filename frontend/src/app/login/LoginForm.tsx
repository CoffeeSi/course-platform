"use client";

import { Button } from "@/components/ui/button";
import { FormEvent, useState } from "react";
import { authApi } from "@/features/auth/api/auth.api";
import { LoginPayload } from "@/features/auth/types/auth.types";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);
    const payload: LoginPayload = {
      email: formData.get('email') as string,
      password: formData.get('password') as string,
    }

    try {
      await authApi.login(payload);

      router.push('/profile');
      router.refresh();
    } catch (err) {
      setError('Неверный email или пароль');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-2 text-sm font-medium">
        Email
        <input
          type="email"
          name="email"
          required
          className="h-10 rounded-md border px-3"
        />
      </label>
      <label className="flex flex-col gap-2 text-sm font-medium">
        Пароль
        <input
          type="password"
          name="password"
          required
          className="h-10 rounded-md border px-3"
        />
      </label>
      {error ? (
        <p className="text-sm text-destructive">Не удалось войти. Проверьте электронную почту и пароль</p>
      ) : null}
      <Button type="submit" disabled={isLoading}>
        {isLoading ? "Logging in..." : "Login"}
      </Button>
    </form>
  )
}