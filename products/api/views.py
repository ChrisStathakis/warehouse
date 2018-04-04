from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from ..models import *
from ..api.serializers import *

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer


class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer

class ProductUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'
