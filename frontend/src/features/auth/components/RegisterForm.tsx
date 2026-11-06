"use client";

import { useState } from "react";
import styles from "@/components/ui/styles/form.module.css";
import type { SubmitEvent } from "react";
import { RegisterPayload } from "@/features/auth/types/auth.types";
import { useRouter } from "next/navigation";
import { authApi } from "@/features/auth/api/auth.api";
import { Button } from "@/components/ui/button";

export default function RegisterForm() {
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const onSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const formData = new FormData(e.currentTarget);
    const payload: RegisterPayload = {
      email: formData.get('email') as string,
      phone_number: formData.get('phone') as string || null,
      password: formData.get('password') as string,
      password_confirm: formData.get('confirmPassword') as string,
    }

    if (payload.password !== payload.password_confirm) {
      setError("Пароли не совпадают");
      return;
    }

    try {
      await authApi.register(payload);

      router.push('/register/verify-email?email=' + payload.email.split('@')[0] + '');
      router.refresh();
    } catch (err) {
      setError(`Ошибка при регистрации: ${err}`);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className={styles.form}>
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
        Телефон
        <input
          type="tel"
          name="phone"
          className={styles.input}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Пароль
        <input
          type="password"
          name="password"
          minLength={8}
          required
          className={styles.input}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Подтвердить пароль
        <input
          type="password"
          name="confirmPassword"
          minLength={8}
          required
          className={styles.input}
        />
      </label>

      {error && (
        <div className="flex flex-col gap-1">
          <p className="text-sm text-destructive">
            {error || "Произошла неизвестная ошибка регистрации"}
          </p>
        </div>
      )}

      <Button type="submit" className={`${styles.button} hover:bg-primary`} disabled={isLoading}>
        {isLoading ? "Создаём аккаунт…" : "Зарегистрироваться"}
      </Button>
    </form>
  );
}
