"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";
import styles from "@/components/ui/styles/form.module.css";
import type { SubmitEvent } from "react";
import { authApi } from "@/features/auth/api/auth.api";
import { LoginPayload } from "@/features/auth/types/auth.types";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
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
    } catch {
      setError('Неверная электронная почта или пароль');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <label className="flex flex-col gap-2 text-sm font-medium">
        Электронная почта
        <input
          type="email"
          name="email"
          required
          className={styles.input}
        />
      </label>
      <label className="flex flex-col gap-2 text-sm font-medium">
        Пароль
        <input
          type="password"
          name="password"
          required
          className={styles.input}
        />
      </label>
      {error ? (
        <p className="text-sm text-destructive">Не удалось войти. Проверьте электронную почту и пароль</p>
      ) : null}
      <Button type="submit" className={`${styles.button} hover:bg-primary`} disabled={isLoading}>
        {isLoading ? "Входим…" : "Войти"}
      </Button>
    </form>
  )
}
