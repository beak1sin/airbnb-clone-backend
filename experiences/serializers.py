from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Experience, Perk
from medias.serializers import PhotoSerializer, VideoSerializer
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer
from wishlists.models import Wishlist


class PerkSerializer(ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"


class ExperienceListSerializer(ModelSerializer):
    rating = SerializerMethodField()
    is_host = SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(read_only=True)

    class Meta:
        model = Experience
        fields = (
            "id",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_host",
            "photos",
            "videos",
        )

    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user


class ExperienceDetailSerializer(ModelSerializer):
    host = TinyUserSerializer(read_only=True)
    perks = PerkSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    photos = PhotoSerializer(many=True, read_only=True)
    videos = VideoSerializer(read_only=True)

    rating = SerializerMethodField()
    is_host = SerializerMethodField()
    is_liked = SerializerMethodField()

    class Meta:
        model = Experience
        fields = "__all__"

    def get_rating(self, experience):
        return experience.rating()

    def get_is_host(self, experience):
        request = self.context["request"]
        return experience.host == request.user

    def get_is_liked(self, experience):
        request = self.context["request"]
        return Wishlist.objects.filter(
            user=request.user, experiences__pk=experience.pk
        ).exists()
