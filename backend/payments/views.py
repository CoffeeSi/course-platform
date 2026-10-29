from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter

from courses.models import Course
from .models import Payment
from .serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer,
)
from .services.payment_service import PaymentService

PaymentCreateResponseSerializer = inline_serializer(
    name="PaymentCreateResponse",
    fields={
        "payment": PaymentSerializer(),
        "checkout": serializers.JSONField(),
    },
)

PaymentWebhookResponseSerializer = inline_serializer(
    name="PaymentWebhookResponse",
    fields={
        "status": serializers.CharField(),
        "payment_id": serializers.IntegerField(),
    },
)


@extend_schema(
    summary="Список платежей",
    description="Получить список платежей текущего пользователя. Для администратора возвращаются все платежи.",
    responses={200: PaymentSerializer(many=True)},
    tags=["Платежи"],
)
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "role", None) == "admin":
            return Payment.objects.select_related("user", "course")
        return Payment.objects.filter(user=user).select_related("user", "course")


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    service_class = PaymentService

    @extend_schema(
        summary="Создать платеж",
        description="Создать платеж для покупки курса и получить данные для перехода к оплате.",
        request=PaymentCreateSerializer,
        responses={201: PaymentCreateResponseSerializer},
        tags=["Платежи"],
    )
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = get_object_or_404(Course, id=serializer.validated_data["course_id"])
        provider_code = serializer.validated_data["provider"]

        try:
            payment, checkout_payload = self.service_class().create_payment(
                user=request.user,
                course=course,
                provider_code=provider_code,
            )
        except ImproperlyConfigured as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        return Response(
            {
                "payment": PaymentSerializer(
                    payment, context={"request": request}
                ).data,
                "checkout": checkout_payload,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    service_class = PaymentService

    @extend_schema(
        summary="Вебхук платежного провайдера",
        description="Обработать callback от платежного провайдера и обновить статус платежа.",
        request=PaymentWebhookSerializer,
        parameters=[
            OpenApiParameter(
                name="provider_code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Код платежного провайдера",
            )
        ],
        responses={200: PaymentWebhookResponseSerializer},
        tags=["Платежи"],
    )
    def post(self, request, provider_code: str):
        if provider_code == Payment.Provider.STRIPE:
            payload = {
                "_raw_body": request.body,
                "_stripe_signature": request.headers.get("Stripe-Signature", ""),
                "_json_body": request.data,
            }
        else:
            serializer = PaymentWebhookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payload = {**dict(request.data), **serializer.validated_data}

        payment = self.service_class().handle_webhook(
            provider_code=provider_code,
            payload=payload,
        )

        return Response(
            {"status": payment.status, "payment_id": payment.id},
            status=status.HTTP_200_OK,
        )


class VerifySessionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Проверить статус сессии оплаты",
        description="Проверить статус сессии оплаты по session_id и получить информацию о платеже.",
        parameters=[
            OpenApiParameter(
                name="session_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="ID сессии оплаты",
            )
        ],
    )
    def get(self, request):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.filter(
            user=request.user, provider_payment_id=session_id
        ).first()

        if not payment:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": payment.status,
                "course_id": payment.course.id if payment.course else None,
            }
        )
