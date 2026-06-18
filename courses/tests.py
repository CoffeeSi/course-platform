from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from courses.models import Category, Course, Module, Lesson


class CourseAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="Password123!",
            role=User.Role.ADMIN,
            is_email_verified=True,
            is_staff=True
        )
        self.instructor = User.objects.create_user(
            email="instructor@example.com",
            password="Password123!",
            role=User.Role.INSTRUCTOR,
            is_email_verified=True
        )
        self.instructor2 = User.objects.create_user(
            email="instructor2@example.com",
            password="Password123!",
            role=User.Role.INSTRUCTOR,
            is_email_verified=True
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="Password123!",
            role=User.Role.STUDENT,
            is_email_verified=True
        )
        
        self.category = Category.objects.create(
            name="Programming",
            slug="programming",
            description="Software Development"
        )
        
        self.course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Python Course",
            description="Learn Python from scratch",
            price=99.99,
            is_published=True
        )
        
        self.module = Module.objects.create(
            course=self.course,
            title="Introduction to Python",
            order=1
        )
        
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="Variables & Data Types",
            content_text="In this lesson...",
            order=1
        )

    def test_category_list_and_create(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            reverse('category-list'),
            {"name": "Design", "slug": "design", "description": "UI/UX Design"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            reverse('category-list'),
            {"name": "Design", "slug": "design", "description": "UI/UX Design"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)

    def test_course_list_and_create(self):
        unpublished_course = Course.objects.create(
            instructor=self.instructor,
            category=self.category,
            title="Unpublished Course",
            description="Not ready yet",
            price=0.00,
            is_published=False
        )
        
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Python Course")
        
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(len(response.data['results']), 1)
        
        self.client.force_authenticate(user=self.instructor)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(len(response.data['results']), 2)
        
        self.client.force_authenticate(user=self.instructor2)
        response = self.client.get(reverse('course-list'))
        self.assertEqual(len(response.data['results']), 1)

        self.client.force_authenticate(user=self.student)
        response = self.client.post(
            reverse('course-list'),
            {"title": "Student Course", "description": "Try to create", "price": 0.00}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.instructor)
        response = self.client.post(
            reverse('course-list'),
            {
                "title": "Django Deep Dive",
                "description": "Learn Django web development",
                "price": 149.99,
                "category_id": self.category.id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_course = Course.objects.get(title="Django Deep Dive")
        self.assertEqual(new_course.instructor, self.instructor)

    def test_course_update_permissions(self):
        self.client.force_authenticate(user=self.instructor2)
        response = self.client.patch(
            reverse('course-detail', kwargs={'pk': self.course.pk}),
            {"title": "Hacked Title"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self.client.force_authenticate(user=self.instructor)
        response = self.client.patch(
            reverse('course-detail', kwargs={'pk': self.course.pk}),
            {"title": "Updated Python Course"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Updated Python Course")

    def test_module_creation_and_ownership(self):
        self.client.force_authenticate(user=self.instructor2)
        response = self.client.post(
            reverse('module-list'),
            {"course": self.course.id, "title": "Hacked Module", "order": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Вы не можете добавлять модули в этот курс", response.data['course'][0])

        self.client.force_authenticate(user=self.instructor)
        response = self.client.post(
            reverse('module-list'),
            {"course": self.course.id, "title": "Module 2: Advanced OOP", "order": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_creation_and_ownership(self):
        self.client.force_authenticate(user=self.instructor2)
        response = self.client.post(
            reverse('lesson-list'),
            {"module": self.module.id, "title": "Hacked Lesson", "order": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Вы не можете добавлять уроки в этот модуль", response.data['module'][0])

        self.client.force_authenticate(user=self.instructor)
        response = self.client.post(
            reverse('lesson-list'),
            {"module": self.module.id, "title": "Lesson 2: Functions", "order": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_restrictions(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('module-list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Необходимо указать параметр запроса 'course'", response.data['detail'])

        response = self.client.get(reverse('module-list') + f"?course={self.course.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(reverse('lesson-list'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Необходимо указать параметр запроса 'module'", response.data['detail'])

        response = self.client.get(reverse('lesson-list') + f"?module={self.module.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('module-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response2 = self.client.get(reverse('lesson-list'))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
