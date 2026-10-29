import client from "@/shared/api/client";
import type {
  CreateCoursePaymentPayload,
  Payment,
  PaymentProvider,
  CreateCoursePaymentResponse,
} from "../types/payment.types";
import { PaginatedResponse } from "@/shared/types/types";

const getPaymentProvider = (): PaymentProvider => {
  const provider = process.env.PAYMENT_PROVIDER?.toLowerCase();

  return provider === "freedompay" ? "freedompay" : "stripe";
};

const isUrlLike = (value: string) => /^https?:\/\//i.test(value) || value.startsWith("/");

const resolveNestedUrl = (value: unknown): string | null => {
  if (!value) {
    return null;
  }

  if (typeof value === "string") {
    return isUrlLike(value) ? value : null;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const nestedUrl = resolveNestedUrl(item);
      if (nestedUrl) {
        return nestedUrl;
      }
    }
    return null;
  }

  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    const prioritizedKeys = [
      "checkout_url",
      "checkoutUrl",
      "payment_url",
      "paymentUrl",
      "redirect_url",
      "redirectUrl",
      "url",
      "href",
    ];

    for (const key of prioritizedKeys) {
      const candidate = record[key];
      if (typeof candidate === "string" && isUrlLike(candidate)) {
        return candidate;
      }
    }

    for (const nestedValue of Object.values(record)) {
      const nestedUrl = resolveNestedUrl(nestedValue);
      if (nestedUrl) {
        return nestedUrl;
      }
    }
  }

  return null;
};

const resolvePaymentUrl = (response: CreateCoursePaymentResponse) => {
  return resolveNestedUrl(response.checkout) || resolveNestedUrl(response.payment) || resolveNestedUrl(response);
};

export const paymentsApi = {
  fetchPayments: (token?: string) => {
    return client.get<PaginatedResponse<Payment>>("/api/v1/payments/", {
      token,
      next: { revalidate: 0 },
    });
  },
  createCoursePayment: async (courseId: number, token?: string) => {
    const payload: CreateCoursePaymentPayload = {
      course_id: courseId,
      provider: getPaymentProvider(),
    };

    const response = await client.post<CreateCoursePaymentResponse>("/api/v1/payments/create/", payload, {
      token,
      next: { revalidate: 0 },
    });

    return {
      paymentUrl: resolvePaymentUrl(response),
      response,
    };
  },
};