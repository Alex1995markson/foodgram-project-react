from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Ingredient
from .serializers import IngredientSerializer
from utils.filters import DoubleSearchBackend


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DoubleSearchBackend]
    search_fields = ['^name', '$name']
    pagination_class = None
