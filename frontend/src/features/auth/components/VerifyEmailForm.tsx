"use client";

import { useEffect, useState } from "react";
import type { SubmitEvent } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/features/auth/api/auth.api";
import { ApiError } from "@/shared/api/client";
import { cardSurface } from "@/components/ui/card";
import styles from "@/components/ui/styles/form.module.css";

export function VerifyEmailForm({ initialEmail }: { initialEmail: string }) {
    const router = useRouter();

    const email = initialEmail;
    const [code, setCode] = useState("");

    const [isVerifying, setIsVerifying] = useState(false);
    const [verifyError, setVerifyError] = useState<string | null>(null);
    const [isVerified, setIsVerified] = useState(false);

    const [isResending, setIsResending] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(0);
    const [resendStatus, setResendStatus] = useState<string | null>(null);
    const [resendError, setResendError] = useState(false);

    useEffect(() => {
        if (resendCooldown <= 0) return;
        const timer = setInterval(() => {
            setResendCooldown((prev) => prev - 1);
        }, 1000);
        return () => clearInterval(timer);
    }, [resendCooldown]);

    const onSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (!email || !code) return;

        setIsVerifying(true);
        setVerifyError(null);

        try {
            await authApi.verifyEmail({ email, code });
            sessionStorage.removeItem("email");
            setIsVerified(true);
        } catch (err: unknown) {
            setVerifyError(
                err instanceof ApiError && err.message
                    ? err.message
                    : "Неверный код. Попробуйте еще раз.",
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
        } catch (err: unknown) {
            const errorMessage =
                err instanceof Error && err.message
                    ? err.message
                    : "Ошибка отправки кода.";
            setResendStatus(errorMessage);
            setResendError(true);
        } finally {
            setIsResending(false);
        }
    };

    if (isVerified) {
        return (
            <main className={`${cardSurface} flex flex-col items-center justify-center min-h-[60vh] max-w-md mx-auto p-6 my-12 text-center`}>
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-6 shadow-sm animate-bounce">
                    <svg
                        className="w-8 h-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                        />
                    </svg>
                </div>
                <h1 className="text-2xl font-bold mb-2 text-foreground">
                    Email успешно подтвержден!
                </h1>
                <p className="text-muted-foreground mb-8 text-sm">
                    Ваш аккаунт успешно активирован. Теперь вы можете
                    пользоваться всеми возможностями платформы.
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
        <main className={`${cardSurface} flex flex-col items-center justify-center min-h-[60vh] max-w-md mx-auto p-6 my-12`}>
            <h1 className="text-2xl font-bold mb-2 text-center text-foreground">
                Подтвердите ваш Email
            </h1>

            <p className="text-muted-foreground text-center mb-6 text-sm">
                Мы отправили письмо с кодом подтверждения на{" "}
                <span className="font-semibold text-foreground break-all">
                    {email || "вашу почту"}
                </span>
                .
            </p>

            <form onSubmit={onSubmit} className={`${styles.form} w-full`}>
                <input
                    type="text"
                    placeholder="Введите код"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    required
                    autoComplete="off"
                    className={`${styles.input} text-center tracking-[0.5em] font-bold bg-background`}
                />

                {verifyError && (
                    <p className="text-sm text-destructive text-center font-medium bg-destructive/10 py-2 px-3 rounded-lg">
                        {verifyError}
                    </p>
                )}

                <button
                    type="submit"
                    disabled={isVerifying || !code}
                    className={`${styles.button} bg-primary text-primary-foreground font-semibold disabled:opacity-50`}
                >
                    {isVerifying ? "Проверка..." : "Подтвердить"}
                </button>
            </form>

            <div className="mt-6 text-center text-sm w-full">
                {resendCooldown > 0 ? (
                    <p className="text-muted-foreground">
                        Отправить код повторно можно через{" "}
                        <span className="font-semibold text-foreground">
                            {resendCooldown}
                        </span>{" "}
                        сек.
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
                    <div
                        className={`mt-3 p-2 rounded-lg text-xs font-semibold ${resendError ? "text-destructive bg-destructive/10" : "text-green-600 bg-green-50"}`}
                    >
                        {resendStatus}
                    </div>
                )}
            </div>
        </main>
    );
}
