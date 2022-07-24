from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from ingredients.views import IngredientsViewSet
from recipes.views import RecipeViewSet
from tags.views import TagsViewSet
from users.views import UserViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'api/tags', TagsViewSet, basename='tags_api')
router_v1.register(r'api/users', UserViewSet, basename='users_api')
router_v1.register(r'api/recipes', RecipeViewSet, basename='recipes_api')
router_v1.register(r'api/ingredients', IngredientsViewSet, basename='ingredients_api')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )

urlpatterns += router_v1.urls
