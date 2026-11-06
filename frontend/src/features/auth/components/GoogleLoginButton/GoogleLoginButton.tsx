"use client";

import { useRef, useState } from "react";
import type { SubmitEvent } from "react";
import { authApi } from "@/features/auth/api/auth.api";
import styles from "./GoogleLoginButton.module.css";
import formStyles from "@/components/ui/styles/form.module.css";

export default function GoogleLoginButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const formRef = useRef<HTMLFormElement>(null);
  const csrfInputRef = useRef<HTMLInputElement>(null);

  async function handleLogin(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setError("");

    try {
      const token = await authApi.getCsrfToken();
      const form = formRef.current;
      const csrfInput = csrfInputRef.current;
      if (!form || !csrfInput) return;

      csrfInput.value = token;
      form.submit();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
      setLoading(false);
    }
  }

  return (
    <form
      ref={formRef}
      method="POST"
      action="/accounts/google/login/"
      onSubmit={handleLogin}
      className={styles.container}
    >
      <input ref={csrfInputRef} type="hidden" name="csrfmiddlewaretoken" />
      <button
        className={`${formStyles.button} ${styles.button}`}
        type="submit"
        disabled={loading}
        aria-busy={loading}
      >
        <span
          className={styles.state}
          aria-hidden="true"
        />
        <span className={styles.contentWrapper}>
          <span className={styles.icon} aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
              <g>
                <path d="M8.00018 3.16667C9.18018 3.16667 10.2368 3.57333 11.0702 4.36667L13.3535 2.08333C11.9668 0.793333 10.1568 0 8.00018 0C4.87352 0 2.17018 1.79333 0.853516 4.40667L3.51352 6.47C4.14352 4.57333 5.91352 3.16667 8.00018 3.16667Z" fill="#EA4335"></path>
                <path d="M15.66 8.18335C15.66 7.66002 15.61 7.15335 15.5333 6.66669H8V9.67335H12.3133C12.12 10.66 11.56 11.5 10.72 12.0667L13.2967 14.0667C14.8 12.6734 15.66 10.6134 15.66 8.18335Z" fill="#4285F4"></path>
                <path d="M3.51 9.53001C3.35 9.04668 3.25667 8.53334 3.25667 8.00001C3.25667 7.46668 3.34667 6.95334 3.51 6.47001L0.85 4.40668C0.306667 5.48668 0 6.70668 0 8.00001C0 9.29334 0.306667 10.5133 0.853333 11.5933L3.51 9.53001Z" fill="#FBBC05"></path>
                <path d="M8.0001 16C10.1601 16 11.9768 15.29 13.2968 14.0633L10.7201 12.0633C10.0034 12.5467 9.0801 12.83 8.0001 12.83C5.91343 12.83 4.14343 11.4233 3.5101 9.52667L0.850098 11.59C2.1701 14.2067 4.87343 16 8.0001 16Z" fill="#34A853"></path>
              </g>
            </svg>
          </span>
          <span className={styles.contents}>
            {loading ? "Перенаправляем…" : "Войти через Google"}
          </span>
        </span>
      </button>
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
