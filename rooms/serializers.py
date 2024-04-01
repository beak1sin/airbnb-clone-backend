from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from wishlists.models import Wishlist


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = (
            "pk",
            "name",
            "description",
        )


class RoomListSerializer(ModelSerializer):
    rating = SerializerMethodField()
    is_owner = SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room

        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
            "photos",
        )
        # depth = 0  # 0(default): rest 프레임워크에 관계 필드들은 기본적으로 id만 보여줌, 1: 관계 필드의 모든 필드, 데이터 보여줌

    # rating 변수명과 동일해야함
    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context.get("request")
        if request:
            return room.owner == request.user
        else:
            return False


class RoomDetailSerializer(ModelSerializer):

    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    rating = SerializerMethodField()
    is_owner = SerializerMethodField()
    is_liked = SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = (
            "pk",
            "owner",
            "amenities",
            "category",
            "rating",
            "is_owner",
            "is_liked",
            "photos",
            "created_at",
            "updated_at",
            "name",
            "country",
            "city",
            "price",
            "rooms",
            "toilets",
            "description",
            "address",
            "pet_friendly",
            "kind",
        )
        # depth = 1

    # rating 변수명과 동일해야함
    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context.get("request")
        if request:
            return room.owner == request.user
        else:
            return False

    def get_is_liked(self, room):
        request = self.context.get("request")
        if request:
            # 로그인 안한 사람들은 인증에서 제외해줘야 에러 안뜸 그치?
            if request.user.is_authenticated:
                return Wishlist.objects.filter(
                    user=request.user, rooms__pk=room.pk
                ).exists()
        return False
