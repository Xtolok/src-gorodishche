from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    AboutDocument,
    ContentSection,
    CurrentActivitySection,
    NokContent,
    HomeStat,
    InfoCard,
    InstitutionProfile,
    LegalSection,
    News,
    Page,
    RegionalSocialCenter,
    ServiceCategory,
    StaffMember,
)


def _base_context(active_page):
    return {'active_page': active_page}


def _page(slug):
    return get_object_or_404(Page, slug=slug)


def _cards(placement):
    return InfoCard.objects.filter(placement=placement)


def _sections(page_slug):
    return ContentSection.objects.filter(page_slug=page_slug).prefetch_related('items')


def _about_context(slug):
    return {
        **_base_context('ob_uchrezhdenii'),
        'page': _page(slug),
    }


def index(request):
    page = _page(Page.SLUG_INDEX)
    ctx = {
        **_base_context('index'),
        'page': page,
        'stats': HomeStat.objects.all(),
        'cards_main': _cards('index_main'),
        'cards_bottom': _cards('index_bottom').exclude(link_url_name='perechen_uslug'),
        'how_to_section': ContentSection.objects.filter(page_slug=Page.SLUG_INDEX).first(),
    }
    return render(request, 'pages/index.html', ctx)


def socialnye_uslugi(request):
    page = _page(Page.SLUG_SOCIAL)
    sections = {s.order: s for s in _sections(Page.SLUG_SOCIAL)}
    ctx = {
        **_base_context('socialnye_uslugi'),
        'page': page,
        'cards': _cards('social_top'),
        'category_sections': [sections[i] for i in (1, 2, 3) if i in sections],
        'full_list_section': sections.get(4),
        'bottom_section': sections.get(10),
    }
    return render(request, 'pages/socialnye-uslugi.html', ctx)


def perechen_uslug(request):
    ctx = {
        **_base_context('socialnye_uslugi'),
        'page': _page(Page.SLUG_PERECHEN),
        'categories': ServiceCategory.objects.prefetch_related('items'),
    }
    return render(request, 'pages/perechen-uslug.html', ctx)


def dnevnoe_otdelenie(request):
    page = _page(Page.SLUG_DNEVNOE)
    sections = {s.order: s for s in _sections(Page.SLUG_DNEVNOE)}
    ctx = {
        **_base_context('socialnye_uslugi'),
        'page': page,
        'cards': _cards('dnevnoe_top'),
        'about_section': sections.get(1),
        'services_section': sections.get(2),
        'how_to_section': sections.get(3),
    }
    return render(request, 'pages/dnevnoe-otdelenie.html', ctx)


def rabota_s_obrascheniyami(request):
    page = _page(Page.SLUG_APPEAL)
    sections = {s.order: s for s in _sections(Page.SLUG_APPEAL)}
    ctx = {
        **_base_context('rabota_s_obrascheniyami'),
        'page': page,
        'appeal_cards': [sections[i] for i in (1, 2) if i in sections],
        'online_section': sections.get(10),
    }
    return render(request, 'pages/rabota-s-obrascheniyami.html', ctx)


def kontakty(request):
    return redirect('ob_uchrezhdenii_kontakty', permanent=True)


def ob_uchrezhdenii(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT),
    }
    return render(request, 'pages/about/index.html', ctx)


def ob_uchrezhdenii_kontakty(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT_CONTACTS),
        'institution': InstitutionProfile.get(),
        'regional_centers': RegionalSocialCenter.objects.all(),
        'contact_docs': AboutDocument.objects.filter(section=AboutDocument.SECTION_CONTACTS),
    }
    return render(request, 'pages/about/kontakty.html', ctx)


def ob_uchrezhdenii_polnomochiya(request):
    sections = {s.order: s for s in _sections(Page.SLUG_ABOUT_POLNOMOCHIYA)}
    ctx = {
        **_about_context(Page.SLUG_ABOUT_POLNOMOCHIYA),
        'tasks_section': sections.get(1),
        'functions_section': sections.get(2),
    }
    return render(request, 'pages/about/polnomochiya.html', ctx)


def ob_uchrezhdenii_rukovodstvo(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT_RUKOVODSTVO),
        'staff': StaffMember.objects.all(),
    }
    return render(request, 'pages/about/rukovodstvo.html', ctx)


def ob_uchrezhdenii_lokalnye_akty(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT_LOKALNYE),
        'documents': AboutDocument.objects.filter(section=AboutDocument.SECTION_RULES),
    }
    return render(request, 'pages/about/documents.html', ctx)


def ob_uchrezhdenii_pravila(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT_PRAVILA),
        'documents': AboutDocument.objects.filter(section=AboutDocument.SECTION_PRAVILA),
    }
    return render(request, 'pages/about/documents.html', ctx)


def ob_uchrezhdenii_popechitelskiy_sovet(request):
    ctx = {
        **_about_context(Page.SLUG_ABOUT_POPECH),
        'documents': AboutDocument.objects.filter(section=AboutDocument.SECTION_POPECH),
    }
    return render(request, 'pages/about/documents.html', ctx)


def novosti(request):
    ctx = {
        **_base_context('novosti'),
        'page': _page(Page.SLUG_NEWS),
        'news_list': News.objects.filter(is_published=True),
    }
    return render(request, 'pages/novosti.html', ctx)


def novosti_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    ctx = {
        **_base_context('novosti'),
        'page': _page(Page.SLUG_NEWS),
        'news': news,
    }
    return render(request, 'pages/novosti-detail.html', ctx)


def pravovye_akty(request):
    ctx = {
        **_base_context('pravovye_akty'),
        'page': _page(Page.SLUG_LEGAL),
    }
    return render(request, 'pages/legal/index.html', ctx)


def pravovye_akty_akty(request):
    ctx = {
        **_base_context('pravovye_akty'),
        'page': _page(Page.SLUG_LEGAL_ACTS),
    }
    return render(request, 'pages/legal/akty.html', ctx)


def pravovye_akty_section(request, slug):
    section = get_object_or_404(LegalSection, slug=slug)
    page_slugs = {
        'ustav': Page.SLUG_LEGAL_USTAV,
        'litsenzii': Page.SLUG_LEGAL_LITSENZII,
        'federal': Page.SLUG_LEGAL_FEDERAL,
        'regional': Page.SLUG_LEGAL_REGIONAL,
        'normativy': Page.SLUG_LEGAL_NORMATIVY,
        'sout': Page.SLUG_LEGAL_SOUT,
    }
    back_url = 'pravovye_akty_akty' if slug in ('federal', 'regional', 'normativy') else 'pravovye_akty'
    ctx = {
        **_base_context('pravovye_akty'),
        'page': _page(page_slugs.get(slug, Page.SLUG_LEGAL)),
        'section': section,
        'back_url': back_url,
    }
    return render(request, 'pages/legal/section.html', ctx)


def tekushchaya_deyatelnost(request):
    ctx = {
        **_base_context('tekushchaya_deyatelnost'),
        'page': _page(Page.SLUG_CURRENT),
        'sections': CurrentActivitySection.objects.all(),
    }
    return render(request, 'pages/current/index.html', ctx)


def tekushchaya_deyatelnost_section(request, slug):
    section = get_object_or_404(CurrentActivitySection, slug=slug)
    ctx = {
        **_base_context('tekushchaya_deyatelnost'),
        'page': _page(Page.SLUG_CURRENT),
        'section': section,
    }
    return render(request, 'pages/current/section.html', ctx)


def nezavisimaya_otsenka_nok(request):
    ctx = {
        **_base_context('nezavisimaya_otsenka_nok'),
        'page': _page(Page.SLUG_NOK),
        'content': NokContent.get(),
    }
    return render(request, 'pages/nok/index.html', ctx)
