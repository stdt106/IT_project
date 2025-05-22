from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
#from news.views import custom_logout


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ex_1.urls')),
    path('news/', include('news.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('users/', include('users.urls')),
    #path('logout/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)