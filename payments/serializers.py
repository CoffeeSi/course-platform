from rest_framework import serializers

from courses.serializers import CourseSerializer
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    course_details = CourseSerializer(source="course", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "course",
            "course_details",
            "provider",
            "status",
            "amount",
            "currency",
            "provider_payment_id",
            "checkout_url",
            "external_reference",
            "metadata",
            "error_message",
            "paid_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "user",
            "status",
            "amount",
            "currency",
            "provider_payment_id",
            "checkout_url",
            "external_reference",
            "metadata",
            "error_message",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class PaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=Payment.Provider.choices)

    def validate_course_id(self, value):
        from courses.models import Course

        if not Course.objects.filter(id=value, is_published=True).exists():
            raise serializers.ValidationError("Курс не найден или не опубликован.")
        return value


class PaymentWebhookSerializer(serializers.Serializer):
    provider_payment_id = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False, allow_blank=True)
    event_type = serializers.CharField(required=False, allow_blank=True)


class PaymentVerifySessionSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=True, max_length=255)
