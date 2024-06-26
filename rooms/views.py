from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import Room, Amenity
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer
import time
from datetime import datetime, timezone, timedelta
from django.utils import timezone as dj_timezone


class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            new_serializer = serializer.save()
            return Response(AmenitySerializer(new_serializer).data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class AmenityDetail(APIView):

    def get_object(self, pk):
        try:
            amenity = Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound
        return amenity

    def get(self, request, pk):
        serializer = AmenitySerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        serializer = AmenitySerializer(
            self.get_object(pk),
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_category = serializer.save()
            return Response(AmenitySerializer(updated_category).data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = RoomDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("Category kind should be 'rooms'")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            # try:
            #     with transaction.atomic():
            #         new_room = serializer.save(
            #             owner=request.user,
            #             category=category,
            #         )
            #         amenities = request.data.get("amenities")
            #         for amenity_pk in amenities:
            #             amenity = Amenity.objects.get(pk=amenity_pk)
            #             new_room.amenities.add(amenity)

            #         return Response(
            #             RoomDetailSerializer(
            #                 new_room,
            #                 context={"request": request},
            #             ).data
            #         )
            # except Exception:
            #     raise ParseError("Amenity not found")
            with transaction.atomic():
                new_room = serializer.save(
                    owner=request.user,
                    category=category,
                )
                amenities = request.data.get("amenities")
                for amenity_pk in amenities:
                    try:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                    except Amenity.DoesNotExist:
                        raise ParseError("Amenity Not found!!")
                    new_room.amenities.add(amenity)

                return Response(
                    RoomDetailSerializer(
                        new_room,
                        context={"request": request},
                    ).data,
                    status=HTTP_200_OK,
                )

        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class RoomDetail(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
        return room

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        room = self.get_object(pk)

        if room.owner != request.user:
            raise PermissionDenied

        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            category_pk = request.data.get("category")

            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("Category kind should be 'rooms'")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")

            with transaction.atomic():
                if category_pk:
                    updated_room = serializer.save(
                        category=category,
                    )
                else:
                    updated_room = serializer.save()

                amenities = request.data.get("amenities")
                if amenities:
                    updated_room.amenities.clear()
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                        updated_room.amenities.add(amenity)
                return Response(
                    RoomDetailSerializer(
                        updated_room,
                        context={"request": request},
                    ).data,
                    status=HTTP_200_OK,
                )
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=HTTP_200_OK)


class RoomReviews(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
        return room

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = ReviewSerializer(room.reviews.all()[start:end], many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        serialzer = ReviewSerializer(data=request.data)
        if serialzer.is_valid():
            review = serialzer.save(
                user=request.user,
                room=self.get_object(pk),
            )
            serialzer = ReviewSerializer(review)
            return Response(serialzer.data)


class RoomAmenities(APIView):

    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
        return room

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1

        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk)
        serializer = AmenitySerializer(room.amenities.all()[start:end], many=True)
        return Response(serializer.data)


class RoomPhotos(APIView):

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class RoomBookings(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        now = dj_timezone.localtime(dj_timezone.now()).date()

        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,
        )
        serializer = PublicBookingSerializer(
            bookings,
            many=True,
        )
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk)
        if ("T" and "Z") in request.data.get("check_in") and (
            "T" and "Z"
        ) in request.data.get("check_out"):
            # Parse the UTC timestamp
            utc_time_1 = datetime.strptime(
                request.data["check_in"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            utc_time_2 = datetime.strptime(
                request.data["check_out"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            # Define the KST timezone as UTC+9
            kst = timezone(timedelta(hours=9))

            # Convert the parsed time to KST
            request.data["check_in"] = (
                utc_time_1.replace(tzinfo=timezone.utc).astimezone(kst).date()
            )
            request.data["check_out"] = (
                utc_time_2.replace(tzinfo=timezone.utc).astimezone(kst).date()
            )

        serializer = CreateRoomBookingSerializer(
            data=request.data,
            context={"room": room},
        )
        if serializer.is_valid():
            new_booking = serializer.save(
                user=request.user,
                room=room,
                kind=Booking.BookingKindChoices.ROOM,
            )
            return Response(
                PublicBookingSerializer(new_booking).data,
                status=HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )


class RoomBookingCheck(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        if Booking.objects.filter(
            room=room,
            check_in__lte=check_out,
            check_out__gte=check_in,
        ).exists():
            return Response({"ok": False})
        else:
            return Response({"ok": True})


def trigger_error(request):
    division_by_zero = 1 / 0
