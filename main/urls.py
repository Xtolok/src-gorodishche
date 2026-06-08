from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('socialnye-uslugi/', views.socialnye_uslugi, name='socialnye_uslugi'),
    path('perechen-uslug/', views.perechen_uslug, name='perechen_uslug'),
    path('dnevnoe-otdelenie/', views.dnevnoe_otdelenie, name='dnevnoe_otdelenie'),
    path('rabota-s-obrascheniyami/', views.rabota_s_obrascheniyami, name='rabota_s_obrascheniyami'),
    path('kontakty/', views.kontakty, name='kontakty'),
    path('ob-uchrezhdenii/', views.ob_uchrezhdenii, name='ob_uchrezhdenii'),
    path('ob-uchrezhdenii/kontakty/', views.ob_uchrezhdenii_kontakty, name='ob_uchrezhdenii_kontakty'),
    path('ob-uchrezhdenii/polnomochiya/', views.ob_uchrezhdenii_polnomochiya, name='ob_uchrezhdenii_polnomochiya'),
    path('ob-uchrezhdenii/rukovodstvo/', views.ob_uchrezhdenii_rukovodstvo, name='ob_uchrezhdenii_rukovodstvo'),
    path('ob-uchrezhdenii/lokalnye-akty/', views.ob_uchrezhdenii_lokalnye_akty, name='ob_uchrezhdenii_lokalnye_akty'),
    path('ob-uchrezhdenii/pravila-rasporyadka/', views.ob_uchrezhdenii_pravila, name='ob_uchrezhdenii_pravila'),
    path(
        'ob-uchrezhdenii/popechitelskiy-sovet/',
        views.ob_uchrezhdenii_popechitelskiy_sovet,
        name='ob_uchrezhdenii_popechitelskiy_sovet',
    ),
    path('novosti/', views.novosti, name='novosti'),
    re_path(r'^novosti/(?P<slug>[-\w]+)/$', views.novosti_detail, name='novosti_detail'),
    path('pravovye-akty/', views.pravovye_akty, name='pravovye_akty'),
    path('pravovye-akty/akty/', views.pravovye_akty_akty, name='pravovye_akty_akty'),
    path('pravovye-akty/<slug:slug>/', views.pravovye_akty_section, name='pravovye_akty_section'),
    path('tekushchaya-deyatelnost/', views.tekushchaya_deyatelnost, name='tekushchaya_deyatelnost'),
    path('tekushchaya-deyatelnost/<slug:slug>/', views.tekushchaya_deyatelnost_section, name='tekushchaya_deyatelnost_section'),
    path('nezavisimaya-otsenka-nok/', views.nezavisimaya_otsenka_nok, name='nezavisimaya_otsenka_nok'),
]
