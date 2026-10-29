// "use client";

// import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
// import { enrollmentsApi } from "../api/enrollmets.api";

// export function useEnrollments() {
//   const { data, isLoading, isError } = useQuery({
//     queryFn: enrollmentsApi.fetchEnrollments,
//     queryKey: ["enrollments"],
//   });

//   const enrollments = data?.results ?? [];
//   return { enrollments, isLoading, isError };
// }

// export function useEnrollmentStatus(courseId: number) {
//   const { data, isLoading, isError } = useQuery({
//     queryFn: () => enrollmentsApi.fetchEnrollmentStatus(courseId),
//     queryKey: ["enrollment-status", courseId],
//     enabled: typeof courseId === "number",
//   });

//   return { status: data, isLoading, isError };
// }

// export function useEnrollToCourse() {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: (courseId: number) => {
//       return enrollmentsApi.enrollToCourse(courseId);
//     },
//     onSuccess: (_data, courseId: number) => {
//       queryClient.invalidateQueries({ queryKey: ["enrollments"] });
//       queryClient.invalidateQueries({ queryKey: ["enrollment-status", courseId] });
//       queryClient.invalidateQueries({ queryKey: ["progress", courseId] });
//     },
//   });
// }

// export function useProgress() {
//   return useQuery({
//     queryKey: ["progress"],
//     queryFn: enrollmentsApi.fetchProgress,
//   });
// }

// export function useMarkProgressComplete() {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: enrollmentsApi.markProgressComplete,
//     onSuccess: () => {
//       queryClient.invalidateQueries({ queryKey: ["progress"] });
//       queryClient.invalidateQueries({ queryKey: ["enrollments"] });
//     },
//   });
// }

// export function useMarkProgressIncomplete() {
//   const queryClient = useQueryClient();

//   return useMutation({
//     mutationFn: enrollmentsApi.markProgressIncomplete,
//     onSuccess: () => {
//       queryClient.invalidateQueries({ queryKey: ["progress"] });
//       queryClient.invalidateQueries({ queryKey: ["enrollments"] });
//     },
//   });
// }
