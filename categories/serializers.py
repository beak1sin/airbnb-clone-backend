from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "pk",
            "name",
            "kind",
        )
        # fields = "__all__"
        # exclude = ("created_at",)


# class CategorySerializer(serializers.Serializer):
#     pk = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(
#         required=True,
#         max_length=50,
#     )
#     kind = serializers.ChoiceField(
#         choices=Category.CategoryKindChoices.choices,
#     )
#     created_at = serializers.DateTimeField(read_only=True)

#     def create(self, validated_data):
#         # Category.objects.create(
#         #     name=validated_data["name"],
#         #     kind=validated_data["kind"],
#         # )
#         # 위 아래 같음 **이 위와 같은 내용을 압축해줌
#         # Category.objects.create(**validated_data)

#         return Category.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         instance.name = validated_data.get("name", instance.name)
#         instance.kind = validated_data.get("kind", instance.kind)
#         instance.save()
#         return instance
