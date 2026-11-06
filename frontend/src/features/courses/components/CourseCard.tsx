import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import Image from "next/image";
import type { Course } from "../types/course.type";

export default function CourseCard(course: Course) {
  return (
    <Card className="overflow-hidden pt-0">
      <Link href={`/courses/${course.id}`} className="relative block aspect-video bg-muted">
        {course.image ? (
          <Image
            src={course.image}
            alt={course.title}
            fill
            unoptimized
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Нет обложки
          </div>
        )}
      </Link>
      <CardHeader>
        <CardTitle>{course.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{course.description}</p>
        <div className="mt-4"></div>
        <div className="flex justify-between">
          <h1 className="text-2xl font-bold">{Number(course.price).toFixed(2)} ₸</h1>
          <Button variant="outline" asChild>
            <Link href={`/courses/${course.id}`}>Перейти к курсу</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
