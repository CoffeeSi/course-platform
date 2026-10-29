import { VideoPlayer } from "@/components/common/player/player";
import { lessonsApi } from "@/features/courses/api/lessons.api";
import { enrollmentsApi } from "@/features/enrollments/api/enrollmets.api";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { ApiError } from "@/shared/api/client";
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from "@/components/ui/breadcrumb";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface Props {
  params: Promise<{ slug: string }>;
}

export default async function LessonPage({ params }: Props) {
  const { slug } = await params;
  const lessonID = Number(slug);

  const token = (await cookies()).get("access_token")?.value;

  let lesson, status;
  try {
    lesson = await lessonsApi.fetchLesson(lessonID, token);
    status = await enrollmentsApi.fetchEnrollmentStatus(lesson.module_detail.course_detail.id, token)
  } catch (error) {
    if (error instanceof ApiError && (error.status === 403 || error.status === 404)) {
      redirect('/courses');
    }
    console.error("Ошибка при загрузке урока:", error)
    return <p className="text-destructive">Lesson not found</p>;
  }

  if (!status.is_enrolled) {
    redirect("/courses")
  }

  return (
    <>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-16">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link href="/courses">Courses</Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link href={`/courses/${lesson.module_detail.course_detail.id}`}>{lesson.module_detail.course_detail.title}</Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{lesson.title}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <div className="flex gap-4">
          {lesson.prev_lesson_id && (
            <Button variant="default" asChild>
              <Link href={`/lessons/${lesson.prev_lesson_id}`}>Previous Lesson</Link>
            </Button>
          )}
          {lesson.next_lesson_id && (
            <Button variant="default" asChild>
              <Link href={`/lessons/${lesson.next_lesson_id}`}>Next Lesson</Link>
            </Button>
          )}
        </div>
        <h1 className="text-4xl font-bold">Lesson</h1>
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-bold">{lesson.title}</h2>
          <p className="text-muted-foreground">{lesson.content_text}</p>
        </div>
        <div className="flex flex-col gap-4">
          <h2 className="text-2xl font-bold">Video</h2>
          <VideoPlayer videoKey={lesson.video_url ?? ""} />
        </div>
      </main>
    </>
  )
}