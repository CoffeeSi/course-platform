import { Metadata } from "next";
import { cookies } from "next/headers";
import { coursesApi } from "@/features/courses/api/courses.api";
import CourseDetails from "@/features/courses/components/CourseDetails";

interface Props {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ payment_error?: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const courseId = Number(slug);
  const token = (await cookies()).get("access_token")?.value;

  try {
    const course = await coursesApi.fetchCourse(courseId, token);
    return {
      title: course.title,
    };
  } catch {
    return {
      title: "Курс",
    };
  }
}

export default async function CoursePage({ params, searchParams }: Props) {
  const { slug } = await params;
  const { payment_error } = await searchParams;
  const courseId = Number(slug);

  return (
    <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-16">
      <CourseDetails courseID={courseId} paymentError={payment_error} />
    </main>
  );
}
