from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trips.views import TripViewSet 

router = DefaultRouter()
router.register(r'trips', TripViewSet) 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]