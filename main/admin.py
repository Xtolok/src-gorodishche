from django.contrib import admin

from .models import (
    AboutDocument,
    ContactInfo,
    ContentSection,
    CurrentActivitySection,
    NokContent,
    HomeStat,
    InfoCard,
    InstitutionProfile,
    LegalItem,
    LegalSection,
    ListItem,
    News,
    Page,
    RegionalSocialCenter,
    ServiceCategory,
    ServiceItem,
    SiteSettings,
    StaffMember,
)


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    list_display = ('site_name', 'footer_text')


@admin.register(ContactInfo)
class ContactInfoAdmin(SingletonAdmin):
    fieldsets = (
        ('Контакты', {
            'fields': (
                'address', 'phone_primary', 'phone_primary_tel',
                'phone_secondary', 'phone_secondary_tel', 'email',
            ),
        }),
        ('Режим работы', {
            'fields': ('work_weekdays', 'work_break', 'work_weekend'),
        }),
        ('Карта', {
            'fields': (
                'show_map',
                'map_latitude',
                'map_longitude',
                'map_zoom',
                'map_iframe',
                'map_placeholder',
            ),
            'description': (
                'Координаты можно взять на yandex.ru/maps (ПКМ по точке → «Что здесь?»). '
                'Либо вставьте готовый iframe из «Поделиться» → «Вставить карту».'
            ),
        }),
        ('Приём граждан', {
            'fields': ('reception_director', 'reception_written', 'reception_online'),
        }),
    )


class ListItemInline(admin.TabularInline):
    model = ListItem
    extra = 1


@admin.register(ContentSection)
class ContentSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_slug', 'order')
    list_filter = ('page_slug',)
    inlines = [ListItemInline]


@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'order')
    ordering = ('order',)


@admin.register(InfoCard)
class InfoCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement', 'order')
    list_filter = ('placement',)
    ordering = ('placement', 'order')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at', 'is_published', 'order')
    list_filter = ('is_published',)
    date_hierarchy = 'published_at'
    prepopulated_fields = {'slug': ('title',)}
    fields = ('title', 'slug', 'body', 'published_at', 'image', 'is_published', 'order')


class LegalItemInline(admin.TabularInline):
    model = LegalItem
    extra = 1
    fields = ('text', 'file', 'external_url', 'order')


@admin.register(LegalSection)
class LegalSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LegalItemInline]


class ServiceItemInline(admin.TabularInline):
    model = ServiceItem
    extra = 1


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    inlines = [ServiceItemInline]


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(SingletonAdmin):
    pass


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'phone', 'order')
    ordering = ('order',)


@admin.register(AboutDocument)
class AboutDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order')
    list_filter = ('section',)
    ordering = ('section', 'order')


@admin.register(NokContent)
class NokContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not NokContent.objects.exists()


@admin.register(CurrentActivitySection)
class CurrentActivitySectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)


@admin.register(RegionalSocialCenter)
class RegionalSocialCenterAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'url')
    ordering = ('number',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('h1', 'slug', 'meta_title')
    list_filter = ('slug',)
