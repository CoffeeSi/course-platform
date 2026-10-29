import client from "@/shared/api/client";
import { Category, Course, CourseDetail, CourseFilters } from "../types/course.type";
import { PaginatedResponse } from "@/shared/types/types";

export const coursesApi = {
    fetchCourses: (filters?: CourseFilters, token?: string) => {
        return client.get<PaginatedResponse<Course>>('/api/v1/courses/', {
            token,
            params: filters,
            next: { revalidate: 0 },
        });

    },
    fetchCategories: (token?: string) => {
        return client.get<PaginatedResponse<Category>>('/api/v1/courses/categories/', {
            token,
            next: { revalidate: 0 },
        });

    },
    fetchCourse: (id: number, token?: string) => {
        return client.get<CourseDetail>(`/api/v1/courses/${id}/`, {
            token,
            next: { revalidate: 0 },
        });
    }
};