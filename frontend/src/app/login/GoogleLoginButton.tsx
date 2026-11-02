"use client";

import { useState } from "react";

export default function GoogleLoginButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/v1/users/csrf/", {
        credentials: "same-origin",
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error("Не удалось подготовить вход");
      }

      const data = await response.json();

      if (typeof data.csrfToken !== "string" || !data.csrfToken) {
        throw new Error("Сервер не вернул CSRF-токен");
      }

      const form = document.createElement("form");
      form.method = "POST";
      form.action = "/accounts/google/login/";

      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "csrfmiddlewaretoken";
      input.value = data.csrfToken;

      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
      setLoading(false);
    }
  }

  return (
    <div>
      <button type="button" onClick={handleLogin} disabled={loading}>
        {loading ? "Перенаправляем…" : "Войти через Google"}
      </button>
      {error && <p role="alert">{error}</p>}
    </div>
  );
}