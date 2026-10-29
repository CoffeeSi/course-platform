import { UserProfile } from "@/features/users/types/users.types";

export type Category = {
    id: number;
    name: string;
    slug: string;
    description: string;
};

export type Course = {
    id: number;
    instructor: UserProfile;
    title: string;
    description: string;
    price: string | number;
    is_published: boolean;
    created_at: string;
    updated_at: string;
    category?: Category;
};

export type CourseShort = Pick<Course, "id" | "title" | "price" | "is_published">;

export type ModuleShort = {
    id: number;
    course: number;
    course_detail: CourseShort;
    title: string;
    order: number;
};

export type Module = ModuleShort & {
    lessons: Lesson[];
};

export type Lesson = {
    id: number;
    module: number;
    module_detail: ModuleShort;
    title: string;
    content_text?: string;
    video_url?: string;
    video_file?: string | null;
    order: number;
    next_lesson_id?: number | null;
    prev_lesson_id?: number | null;
    is_free: boolean;
    created_at: string;
};

export type CourseDetail = Course & {
    modules: Module[];
};

export type CourseFilters = {
    page?: number;
    category_id?: number;
    instructor_id?: number;
};
