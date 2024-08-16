from events.models import Draw
from rest_framework.generics import UpdateAPIView

from .serializers import DrawSerializer


class UpdateDrawCollected(UpdateAPIView):
    queryset = Draw.objects.all()
    lookup_field = "pk"
    serializer_class = DrawSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
