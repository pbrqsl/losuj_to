from django.urls import path

from .views import UpdateDrawCollected

urlpatterns = [
    path("draw_collected/<int:pk>", UpdateDrawCollected.as_view(), name="collect_draw")
]
