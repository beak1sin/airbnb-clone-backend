from django.urls import path
from . import views

urlpatterns = [
    path("", views.Categories.as_view()),
    path("<int:pk>", views.CategoryDetail.as_view()),
]


# viewset일때
# urlpatterns = [
#     path(
#         "",
#         views.CategoryViewSet.as_view(
#             {
#                 "get": "list",
#                 "post": "create",
#             }
#         ),
#     ),
#     path(
#         # pk라고 꼭 해야함
#         "<int:pk>",
#         views.CategoryViewSet.as_view(
#             {
#                 "get": "retrieve",
#                 "put": "partial_update",
#                 "delete": "destroy",
#             }
#         ),
#     ),
# ]
