import type { Course, Lesson } from "@/features/courses/types/course.type";
import type { UserProfile } from "@/features/users/types/users.types";

export type Enrollment = {
  id: number;
  student: UserProfile;
  course: Course;
  course_details: Course;
  progress: Progress[];
  enrolled_at: string;
};

export type EnrollmentCreate = {
  id: number;
  course: number;
  enrolled_at: string;
};

export type Progress = {
  id: number;
  enrollment: number;
  lesson: number;
  lesson_details: Lesson;
  is_completed: boolean;
  completed_at: string | null;
};

export type EnrollmentStatus = {
  course_id: number;
  is_enrolled: boolean;
  progress_percent: number;
}