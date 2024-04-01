from django.utils import timezone
from rest_framework import serializers
from .models import Booking


class CreateRoomBookingSerializer(serializers.ModelSerializer):

    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if value > now:
            return value
        else:
            raise serializers.ValidationError("체크인은 오늘보다 하루 뒤여야 합니다!")

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if value > now:
            return value
        else:
            raise serializers.ValidationError("체크아웃은 오늘보다 하루 뒤여야 합니다!")

    def validate(self, data):
        room = self.context.get("room")
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError("체크인이 체크아웃보다 먼저와야합니다!")

        if Booking.objects.filter(
            room=room,
            check_in__lte=data["check_out"],
            check_out__gte=data["check_in"],
        ).exists():
            raise serializers.ValidationError("이미 예약된 방입니다.")

        return data


class CreateExperienceBookingSerializer(serializers.ModelSerializer):
    experience_time_start = serializers.DateTimeField()
    experience_time_end = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = (
            "experience_time_start",
            "experience_time_end",
            "guests",
        )

    def validate_experience_time_start(self, data):
        start = data.date()
        now = timezone.localtime(timezone.now()).date()
        if start > now:
            return data
        else:
            raise serializers.ValidationError("예약은 오늘보다 하루 뒤여야 합니다!")

    def validate_experience_time_end(self, data):
        end = data.date()
        now = timezone.localtime(timezone.now()).date()
        if end > now:
            return data
        else:
            raise serializers.ValidationError("예약은 오늘보다 하루 뒤여야 합니다!")

    def validate(self, data):
        if data["experience_time_end"] <= data["experience_time_start"]:
            raise serializers.ValidationError("예약 종료 시간이 뒤로 가야합니다!")

        if Booking.objects.filter(
            experience_time_start__lt=data["experience_time_end"],
            experience_time_end__gt=data["experience_time_start"],
        ).exists():
            raise serializers.ValidationError("이미 예약된 시간입니다.")

        return data


class UpdateExperienceBookingSerializer(serializers.ModelSerializer):
    experience_time_start = serializers.DateTimeField()
    experience_time_end = serializers.DateTimeField()

    class Meta:
        model = Booking
        fields = (
            "experience_time_start",
            "experience_time_end",
            "guests",
        )

    def validate_experience_time_start(self, data):
        start = data.date()
        now = timezone.localtime(timezone.now()).date()
        if start > now:
            return data
        else:
            raise serializers.ValidationError("예약은 오늘보다 하루 뒤여야 합니다!")

    def validate_experience_time_end(self, data):
        end = data.date()
        now = timezone.localtime(timezone.now()).date()
        if end > now:
            return data
        else:
            raise serializers.ValidationError("예약은 오늘보다 하루 뒤여야 합니다!")

    def validate(self, data):
        if "experience_time_end" in data and "experience_time_start" in data:
            if data["experience_time_end"] <= data["experience_time_start"]:
                raise serializers.ValidationError("예약 종료 시간이 뒤로 가야합니다!")

            if Booking.objects.filter(
                experience_time_start__lt=data["experience_time_end"],
                experience_time_end__gt=data["experience_time_start"],
            ).exists():
                raise serializers.ValidationError("이미 예약된 시간입니다.")

            return data
        return data


class PublicBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time_start",
            "experience_time_end",
            "guests",
        )
