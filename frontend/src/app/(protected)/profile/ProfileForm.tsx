'use client';

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { usersApi } from "@/features/users/api/users.api";

export function ProfileForm({ initialData }: { initialData: any }) {
  const [isPending, setIsPending] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isError, setIsError] = useState(false);

  const router = useRouter();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
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
    } catch (error) {
      setIsError(true);
    } finally {
      setIsPending(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-2 text-sm font-medium">
        Имя
        <input
          name="first_name"
          defaultValue={initialData?.first_name ?? ""}
          className="h-10 rounded-md border px-3"
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Фамилия
        <input
          name="last_name"
          defaultValue={initialData?.last_name ?? ""}
          className="h-10 rounded-md border px-3"
        />
      </label>

      <label className="flex flex-col gap-2 text-sm font-medium">
        Аватар (URL)
        <input
          name="avatar"
          defaultValue={initialData?.avatar ?? ""}
          className="h-10 rounded-md border px-3"
        />
      </label>

      {isSuccess && <p className="text-sm text-green-600">Профиль успешно обновлен</p>}
      {isError && <p className="text-sm text-destructive">Не удалось обновить профиль</p>}

      <Button type="submit" disabled={isPending}>
        {isPending ? "Saving..." : "Save profile"}
      </Button>
    </form>
  );
}