from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import (
    PerkSerializer,
    ExperienceListSerializer,
    ExperienceDetailSerializer,
)
from .models import Perk, Experience
from bookings.models import Booking
from categories.models import Category
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer, VideoSerializer
from bookings.serializers import (
    PublicBookingSerializer,
    CreateExperienceBookingSerializer,
    UpdateExperienceBookingSerializer,
)
from datetime import datetime


class Experiences(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_experiences = Experience.objects.all()
        serializer = ExperienceListSerializer(
            all_experiences,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = ExperienceDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required!!")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.ROOMS:
                    raise ParseError("Category kind should be 'experiences'")
            except Category.DoesNotExist:
                raise ParseError("category not found!!")
            # try:
            #     with transaction.atomic():
            #         new_experience = serializer.save(
            #             host=request.user,
            #             category=category,
            #         )
            #         perks = request.data.get("perks")
            #         for perk_pk in perks:
            #             perk = Perk.objects.get(pk=perk_pk)
            #             new_experience.perks.add(perk)

            #         return Response(ExperienceDetailSerializer(new_experience).data)
            # except Exception:
            #     raise ParseError("Perk Not Found!")
            with transaction.atomic():
                new_experience = serializer.save(
                    host=request.user,
                    category=category,
                )
                perks = request.data.get("perks")
                for perk_pk in perks:
                    try:
                        perk = Perk.objects.get(pk=perk_pk)
                    except Perk.DoesNotExist:
                        raise ParseError("Perk not found")
                    new_experience.perks.add(perk)

                return Response(
                    ExperienceDetailSerializer(
                        new_experience,
                        context={"request": request},
                    ).data
                )
        else:
            return Response(serializer.errors)


class ExperienceDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            experience = Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
        return experience

    def get(self, request, pk):
        experience = self.get_object(pk)
        serializer = ExperienceDetailSerializer(
            experience, context={"request": request}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        serializer = ExperienceDetailSerializer(
            experience,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.ROOMS:
                        raise ParseError("Category kind should be 'experiences'")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
            with transaction.atomic():
                if category_pk:
                    updated_experience = serializer.save(
                        category=category,
                    )
                else:
                    updated_experience = serializer.save()

                perks = request.data.get("perks")
                if perks:
                    updated_experience.perks.clear()
                    for perk_pk in perks:
                        perk = Perk.objects.get(pk=perk_pk)
                        updated_experience.perks.add(perk)
                return Response(
                    ExperienceDetailSerializer(
                        updated_experience,
                        context={"request": request},
                    ).data
                )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        experience = self.get_object(pk)
        if experience.host != request.user:
            raise PermissionDenied
        experience.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class ExperiencePerks(APIView):
    def get_object(self, pk):
        try:
            experience = Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
        return experience

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        experience = self.get_object(pk)
        serializer = PerkSerializer(experience.perks.all()[start:end], many=True)
        return Response(serializer.data)


class ExperienceReviews(APIView):
    def get_object(self, pk):
        try:
            experience = Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
        return experience

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        experience = self.get_object(pk)
        serializer = ReviewSerializer(experience.reviews.all()[start:end], many=True)
        return Response(serializer.data)


class ExperiencePhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        experience = self.get_object(pk)
        if request.user != experience.host:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(experience=experience)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceVideos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        experience = self.get_object(pk)
        if request.user != experience.host:
            raise PermissionDenied
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            video = serializer.save(experience=experience)
            serializer = VideoSerializer(video)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ExperienceBookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        experience = self.get_object(pk)
        now = timezone.localtime(timezone.now())
        bookings = Booking.objects.filter(
            experience=experience,
            kind=Booking.BookingKindChoices.EXPERIENCE,
            experience_time_start__gt=now,
        )
        serializer = PublicBookingSerializer(
            bookings,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        experience = self.get_object(pk)
        serializer = CreateExperienceBookingSerializer(data=request.data)
        if serializer.is_valid():
            new_booking = serializer.save(
                user=request.user,
                experience=experience,
                kind=Booking.BookingKindChoices.EXPERIENCE,
            )
            return Response(PublicBookingSerializer(new_booking).data)
        else:
            return Response(serializer.errors)


class ExperienceBookingDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound

    def get(self, request, pk, booking_pk):
        experience = self.get_object(pk)
        try:
            booking = Booking.objects.get(experience=experience, pk=booking_pk)
        except Booking.DoesNotExist:
            raise NotFound
        serializer = PublicBookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, pk, booking_pk):
        experience = self.get_object(pk)
        booking = Booking.objects.get(experience=experience, pk=booking_pk)
        if booking.user != request.user:
            raise PermissionDenied
        serializer = UpdateExperienceBookingSerializer(
            booking,
            data=request.data,
            # partial=True,
        )
        if serializer.is_valid():
            updated_booking = serializer.save()
            return Response(PublicBookingSerializer(updated_booking).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk, booking_pk):
        experience = self.get_object(pk)
        booking = Booking.objects.get(experience=experience, pk=booking_pk)
        if booking.user != request.user:
            raise PermissionDenied
        booking.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Perks(APIView):
    def get(self, request):
        all_perks = Perk.objects.all()
        serializer = PerkSerializer(all_perks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PerkSerializer(data=request.data)
        if serializer.is_valid():
            new_serializer = serializer.save()
            return Response(PerkSerializer(new_serializer).data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):

    def get_object(self, pk):
        try:
            perk = Perk.objects.get(pk=pk)
        except Perk.DoesNotExist:
            raise NotFound
        return perk

    def get(self, request, pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request, pk):
        perk = self.get_object(pk)
        serializer = PerkSerializer(
            perk,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_serializer = serializer.save()
            return Response(PerkSerializer(updated_serializer).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=HTTP_204_NO_CONTENT)
