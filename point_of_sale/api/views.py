from .serializers import *

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticated


class RetailOrderListApiView(ListCreateAPIView):
    queryset = RetailOrder.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RetailOrderSerializer



class RetailOrderRetrieveUpdateDestroyApiView(RetrieveUpdateAPIView):
    queryset = RetailOrder.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RetailOrderSerializer
    # lookup_field = 'pk'




