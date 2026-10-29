import CourseDetails from "@/features/courses/components/CourseDetails";

interface Props {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ payment_error?: string }>;
}

export default async function CoursePage({ params, searchParams }: Props) {
  const { slug } = await params;
  const { payment_error } = await searchParams;
  const courseId = Number(slug);

  return (
    <>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-16">
        <CourseDetails courseID={courseId} paymentError={payment_error} />
      </main>
    </>
  )
}
