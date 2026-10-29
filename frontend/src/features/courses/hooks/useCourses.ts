// 'use client';
//
// import { useQuery } from '@tanstack/react-query';
// import { CourseFilters } from '../types/course.type';
// import { coursesApi } from '../api/courses.api';
//
//
// export function useCourses(filters?: CourseFilters) {
//     const { data, isLoading, isError } = useQuery({
//         queryKey: ['courses', filters],
//         queryFn: () => coursesApi.fetchCourses(filters),
//     });
//     const courses = data?.results ?? [];
//     return { courses, count: data?.count ?? 0, isLoading, isError };
// }
//
// export function useCourse(id: number) {
//     const { data, isLoading, isError } = useQuery({
//         queryKey: ['courses', id],
//         queryFn: () => coursesApi.fetchCourse(id),
//         enabled: Number.isFinite(id),
//     });
//     return { course: data, isLoading, isError };
// }
//
// export function useCategories() {
//     const { data, isLoading, isError } = useQuery({
//         queryKey: ['categories'],
//         queryFn: coursesApi.fetchCategories,
//     });
//
//     return {
//         categories: data?.results ?? [],
//         isLoading,
//         isError,
//     };
// }
