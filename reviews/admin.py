from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from .models import Review


class WordFilter(admin.SimpleListFilter):
    title = "filter by words!"
    parameter_name = "word"

    def lookups(self, request, model_admin):
        return [
            ("good", "Good"),
            ("great", "Great"),
            ("awesome", "Awesome"),
        ]

    def queryset(self, request, reviews):
        word = self.value()
        if word:
            return reviews.filter(payload__contains=word)
        else:
            return reviews


class goodOrBad(admin.SimpleListFilter):
    title = "good or bad reviews!"

    parameter_name = "gob"

    def lookups(self, request, model_admin):
        return [("good", "Good"), ("bad", "Bad")]

    def queryset(self, request, queryset):
        gob = self.value()
        if gob:
            if gob == "good":
                return queryset.filter(rating__gte=3)
            else:
                return queryset.filter(rating__lt=3)
        else:
            return queryset


# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "room",
        "experience",
        "payload",
    )

    list_filter = (
        WordFilter,
        goodOrBad,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly",
    )
