import type { Course } from "@/features/courses/types/course.type";

export type PaymentProvider = "stripe" | "freedompay";

export type PaymentStatus =
  | "pending"
  | "processing"
  | "succeeded"
  | "failed"
  | "canceled"
  | "refunded";

export type CreateCoursePaymentPayload = {
  course_id: number;
  provider: PaymentProvider;
};

export type Payment = {
  id: number;
  user: number;
  course: number;
  course_details: Course;
  provider: PaymentProvider;
  status: PaymentStatus;
  amount: string;
  currency: string;
  provider_payment_id: string | null;
  checkout_url: string;
  external_reference: string;
  metadata: unknown;
  error_message: string;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
};

export type CreateCoursePaymentResponse = {
  payment: Payment;
  checkout: string | { checkout_url?: string; url?: string; payment_url?: string };
};