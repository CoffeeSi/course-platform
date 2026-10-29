import CourseList from "@/features/courses/components/CourseList";

export default async function CoursesPage() {
  return (
    <>
      <main className="flex flex-col w-full max-w-7xl justify-center mx-auto my-16 dark:bg-black sm:items-start">
        <h1 className="scroll-m-20 text-center text-4xl font-extrabold tracking-tight text-balance">Курсы</h1>
        <div className="mb-8"></div>
        <CourseList />
      </main>
    </>
  )
}