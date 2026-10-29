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

    def test_category_detail_update_and_delete(self):
        response = self.client.get(reverse('category-detail', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], "programming")

        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            reverse('category-detail', kwargs={'pk': self.category.pk}),
            {"description": "Updated description"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.description, "Updated description")

        response = self.client.delete(reverse('category-detail', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())

    def test_course_detail_and_delete(self):
        response = self.client.get(reverse('course-detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Python Course")
        self.assertEqual(len(response.data['modules']), 1)

        self.client.force_authenticate(user=self.instructor)
        response = self.client.delete(reverse('course-detail', kwargs={'pk': self.course.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

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

    def test_module_detail_update_and_delete(self):
        response = self.client.get(reverse('module-detail', kwargs={'pk': self.module.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Introduction to Python")

        self.client.force_authenticate(user=self.instructor)
        response = self.client.patch(
            reverse('module-detail', kwargs={'pk': self.module.pk}),
            {"title": "Updated Module"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module.refresh_from_db()
        self.assertEqual(self.module.title, "Updated Module")

        response = self.client.delete(reverse('module-detail', kwargs={'pk': self.module.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Module.objects.filter(pk=self.module.pk).exists())

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

    def test_lesson_detail_update_and_delete(self):
        response = self.client.get(reverse('lesson-detail', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Variables & Data Types")

        self.client.force_authenticate(user=self.instructor)
        response = self.client.patch(
            reverse('lesson-detail', kwargs={'pk': self.lesson.pk}),
            {"title": "Updated Lesson"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Updated Lesson")

        response = self.client.delete(reverse('lesson-detail', kwargs={'pk': self.lesson.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

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
