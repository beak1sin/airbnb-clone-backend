from django.contrib import admin
from .models import Room, Amenity


@admin.action(description="price를 0으로 바꿈")
def reset_prices(model_admin, request, rooms):
    for room in rooms.all():
        room.price = 0
        room.save()


@admin.register(Room)
# Register your models here.
class RoomAdmin(admin.ModelAdmin):

    actions = (reset_prices,)
    list_display = (
        "name",
        "price",
        "kind",
        "rating",
        "total_amenities",
        "owner",
        "created_at",
    )

    list_filter = (
        "country",
        "city",
        "pet_friendly",
        "kind",
        "amenities",
        "created_at",
    )

    search_fields = (
        "name",
        "=price",
        "^owner__username",
    )

    # models.py 에서 함수를 만드는거랑 동일한 방식
    # def total_amenities(self, room):
    #     return room.amenities.count()


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
