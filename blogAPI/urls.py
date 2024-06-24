from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version='v1',
        description="This Project handles dealing with Blog in basic API env",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
]

blog_urlpatterns = [
    path('', include('blog.urls')),
    path('accounts/', include('core.urls')),
]

api_urlpatterns = [
    path("api/v1/", include(blog_urlpatterns)),
]

urlpatterns += api_urlpatterns