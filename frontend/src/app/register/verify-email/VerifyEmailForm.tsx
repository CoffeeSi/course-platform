"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/features/auth/api/auth.api";

export function VerifyEmailForm({ initialEmail }: { initialEmail?: string }) {
  const router = useRouter();

  const [email, setEmail] = useState(initialEmail ?? "");
  const [code, setCode] = useState("");

  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [isVerified, setIsVerified] = useState(false);

  const [isResending, setIsResending] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resendStatus, setResendStatus] = useState<string | null>(null);
  const [resendError, setResendError] = useState(false);

  useEffect(() => {
    if (initialEmail) return;
    const emailFromStorage = sessionStorage.getItem("email");
    if (emailFromStorage) setEmail(emailFromStorage);
  }, [initialEmail]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!email || !code) return;

    setIsVerifying(true);
    setVerifyError(null);

    try {
      await authApi.verifyEmail({ email, code });
      sessionStorage.removeItem("email");
      setIsVerified(true);
    } catch (err: any) {
      const errorData = err?.response?.data;
      setVerifyError(
        errorData?.error || errorData?.detail || "Неверный код. Попробуйте еще раз."
      );
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    if (!email || resendCooldown > 0) return;

    setIsResending(true);
    setResendStatus(null);
    setResendError(false);

    try {
      await authApi.resendEmailVerification(email);
      setResendCooldown(60);
      setResendStatus("Новый код отправлен на ваш Email.");
      setResendError(false);
    } catch (err: any) {
      const errorData = err?.response?.data;
      const errorMessage =
        errorData?.error || errorData?.detail || err?.message || "Ошибка отправки кода.";
      setResendStatus(errorMessage);
      setResendError(true);
    } finally {
      setIsResending(false);
    }
  };

  if (isVerified) {
    return (
      <main className="flex flex-col items-center justify-center min-h-[60vh] max-w-md mx-auto p-4 text-center">
        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6 shadow-sm animate-bounce">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-2 text-foreground">Email успешно подтвержден!</h1>
        <p className="text-muted-foreground mb-8 text-sm">
          Ваш аккаунт успешно активирован. Теперь вы можете пользоваться всеми возможностями платформы.
        </p>
        <button
          onClick={() => {
            router.push("/");
            router.refresh();
          }}
          className="w-full py-2.5 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-all shadow-sm"
        >
          Продолжить работу
        </button>
      </main>
    );
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-[60vh] max-w-md mx-auto p-6 border rounded-2xl shadow-sm bg-card my-12">
      <h1 className="text-2xl font-bold mb-2 text-center text-foreground">Подтвердите ваш Email</h1>

      <p className="text-muted-foreground text-center mb-6 text-sm">
        Мы отправили письмо с кодом подтверждения на{" "}
        <span className="font-semibold text-foreground break-all">{email || "вашу почту"}</span>.
      </p>

      <form onSubmit={onSubmit} className="w-full flex flex-col gap-4">
        <input
          type="text"
          placeholder="Введите код"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
          autoComplete="off"
          className="border p-3.5 rounded-lg w-full text-center tracking-[0.5em] font-bold text-2xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all bg-background"
        />

        {verifyError && (
          <p className="text-sm text-destructive text-center font-medium bg-destructive/10 py-2 px-3 rounded-lg">
            {verifyError}
          </p>
        )}

        <button
          type="submit"
          disabled={isVerifying || !code}
          className="w-full py-2.5 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-all shadow-sm"
        >
          {isVerifying ? "Проверка..." : "Подтвердить"}
        </button>
      </form>

      <div className="mt-6 text-center text-sm w-full">
        {resendCooldown > 0 ? (
          <p className="text-muted-foreground">
            Отправить код повторно можно через <span className="font-semibold text-foreground">{resendCooldown}</span> сек.
          </p>
        ) : (
          <button
            type="button"
            onClick={handleResend}
            disabled={isResending || !email}
            className="text-primary hover:text-primary/80 underline font-medium focus:outline-none disabled:opacity-50 transition-all"
          >
            {isResending ? "Отправка..." : "Отправить код повторно"}
          </button>
        )}

        {resendStatus && (
          <div className={`mt-3 p-2 rounded-lg text-xs font-semibold ${resendError ? "text-destructive bg-destructive/10" : "text-green-600 bg-green-50"}`}>
            {resendStatus}
          </div>
        )}
      </div>
    </main>
  );
}
