"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function PaymentStatusHandler({ sessionId }: { sessionId?: string }) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'failed'>('loading');
  const router = useRouter();

  useEffect(() => {
    if (!sessionId) {
      setStatus('error');
      return;
    }

    let attempts = 0;
    const maxAttempts = 30;

    const interval = setInterval(async () => {
      attempts++;

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/payments/verify-session/?session_id=${sessionId}`, {
          credentials: 'include'
        });

        if (!res.ok) return;

        const data = await res.json();

        if (data.status === 'succeeded') {
          clearInterval(interval);
          setStatus('success');
          router.push(`/courses/${data.course_id}`);
        }
        else if (['failed', 'canceled'].includes(data.status)) {
          clearInterval(interval);
          setStatus('failed');
        }
      } catch (err) {
        console.error("Ошибка поллинга:", err);
      }

      if (attempts >= maxAttempts) {
        clearInterval(interval);
        setStatus('error');
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [sessionId, router]);

  if (status === 'error') return <p className="text-red-500">Время ожидания истекло. Пожалуйста, проверьте почту или свяжитесь с поддержкой.</p>;
  if (status === 'failed') return <p className="text-red-500">Оплата не удалась или была отменена.</p>;

  return (
    <div className="text-center">
      <p className="text-muted-foreground">
        {status === 'loading' ? "Проверяем статус платежа..." : "Перенаправляем к курсу..."}
      </p>
    </div>
  );
}