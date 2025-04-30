from django.urls import path

from . import views

app_name = 'bmc'
urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('<int:journal>/search/', views.search, name='search'),
    # path('<int:journal>/search/afterselect/', views.after_select, name='afterselect'),
    path('<int:journal>/search/result/', views.result, name='result'),
    path('<int:journal>/search/save/', views.save, name='save'),
    path('<int:journal>/search/download/', views.download_pdf, name='download'),
    path('<int:journal>/search/static/', views.static_result, name='static')
]
