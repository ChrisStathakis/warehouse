def set_active(modeladmin, request, queryset):
    queryset.update(active=True)
set_active.short_description = 'Active'


def set_not_active(modeladmin, request, queryset):
    queryset.update(active=False)
set_not_active.short_description = 'Non active'


def set_first_page(modeladmin, request, queryset):
    queryset.update(show_on_menu=True)
set_first_page.short_description = 'Active on NavBar'


def set_not_first_page(modeladmin, request, queryset):
    queryset.update(show_on_menu=False)
set_not_first_page.short_description = 'Non Active on Navbar'