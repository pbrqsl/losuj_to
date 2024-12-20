from events.models import Draw, Wish
from rest_framework import serializers


class DrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draw
        fields = ["collected"]
        read_only_fields = []

    def update(self, instance, validated_data):
        instance.collected = validated_data.get("collected", instance.collected)
        instance.save()
        return instance


class WishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
