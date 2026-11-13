'use client';

import { useState } from "react";
import styles from "@/components/ui/styles/form.module.css";
import type { SubmitEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { usersApi } from "@/features/users/api/users.api";
import type { UserProfile } from "@/features/users/types/users.types";

export function ProfileForm({ initialData }: { initialData: UserProfile["profile"] }) {
  const [isPending, setIsPending] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isError, setIsError] = useState(false);

  const router = useRouter();

  const handleSubmit = async (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsPending(true);
    setIsSuccess(false);
    setIsError(false);

    const formData = new FormData(event.currentTarget);
    const payload = {
      profile: {
        first_name: String(formData.get("first_name") ?? ""),
        last_name: String(formData.get("last_name") ?? ""),
        avatar: String(formData.get("avatar") ?? ""),
      }
    };

    try {
      await usersApi.updateProfile(payload);
      setIsSuccess(true);
      router.refresh();
    } catch {
      setIsError(true);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <label className="flex flex-col gap-2 text-sm font-medium">
        Имя
        <input
          name="first_name"
          defaultValue={initialData?.first_name ?? ""}
          className={styles.input}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Фамилия
        <input
          name="last_name"
          defaultValue={initialData?.last_name ?? ""}
          className={styles.input}
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Аватар (URL)
        <input
          name="avatar"
          defaultValue={initialData?.avatar ?? ""}
          className={styles.input}
        />
      </label>

      {isSuccess && <p className="text-sm text-green-600">Профиль успешно обновлен</p>}
      {isError && <p className="text-sm text-destructive">Не удалось обновить профиль</p>}

      <Button type="submit" className={`${styles.button} hover:bg-primary`} disabled={isPending}>
        {isPending ? "Сохраняем…" : "Сохранить профиль"}
      </Button>
    </form>
  );
}
