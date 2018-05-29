from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
from .forms import ProductAdminForm
from .admin_actions import *
from mptt.admin import MPTTModelAdmin, DraggableMPTTAdmin

# Register your models here.


def is_featured_action(modeladmin, request, queryset):
    queryset.update(is_featured=True)
is_featured_action.short_descriprion = 'Featured Active'


def is_not_featured_action(modeladmin, request, queryset):
    queryset.update(is_featured=False)
is_not_featured_action.short_description = 'Featured Deactive'


def non_site_active(modeladmin, request, queryset):
    queryset.update(status=False)
    queryset.update(site_active=False)
non_site_active.short_description = ' Απενεργοποίηση Προϊόντος'


def site_active(modeladmin, request, queryset):
    queryset.update(status=True)
    queryset.update(site_active=True)
site_active.short_description = 'Eνεργοποίηση Προϊόντος'


class ImageInline(admin.TabularInline):
    model = ProductPhotos
    extra = 3


class CharacteristicsInline(admin.TabularInline):
    model = ProductCharacteristics
    extra = 3


class SizeAttributeInline(admin.TabularInline):
   model = SizeAttribute
   extra = 5
        

@admin.register(SizeAttribute)
class SizeAttributeAdmin(admin.ModelAdmin):
   readonly_fields = ['tag_final_price'] 
   list_display = ['product_related' , 'title', 'qty', 'tag_final_price']
   list_filter = ['product_related', 'title']
   search_fields = ['product_related__title', 'product_related__color__title']
   fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields': (
                      ('product_related', 'title'),
                      ('price_buy', 'order_discount', 'qty',),
                      'tag_final_price',  
                    )
            }),
        )
 

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['title']


@admin.register(CategorySite)
class CategorySiteAdmin(ImportExportModelAdmin):
    list_display = ['title', 'parent', 'active', 'show_on_menu']
    list_filter = ['active', 'show_on_menu', 'parent']
    readonly_fields = ['image_tag', 'image_tag_tiny']
    actions = [set_active, set_not_active, set_first_page, set_not_first_page]
    fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields': (('active', 'show_on_menu'),
                      ('image_tag', 'image'),
                      ('title',),
                      ('content',),
                      'parent',
                      )
        }),
        ('SEO',{
            'classes':('collapse',),
            'fields':(('slug', 'meta_description',))
        }),
    )


@admin.register(Brands)
class BrandAdmin(ImportExportModelAdmin):
    search_fields = ['title']
    list_display = ['image_tag_tiny', 'title', 'active']
    list_filter = ['active']
    readonly_fields = ['image_tag']
    fields = ['title', 'active', 'image_tag', 'image', 'meta_description', 'slug']


class ProductCharacteristicAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    list_display = ['title', 'content_type', 'description']
    search_fields = ['title','content_type', 'description']
    fields = ['title', 'content_type', 'description']


class ProductAdmin(ImportExportModelAdmin):
    form = ProductAdminForm
    save_as = True
    search_fields = ['title', 'brand__title', 'category_site__title', 'sku', 'color__title']
    readonly_fields = ['image_tag', 'image_back_tag', 'tag_final_price', ]
    list_display = ['title', 'active', 'is_featured', 'qty', 'tag_final_price', 'category', 'brand', 'vendor']
    list_filter = ['status', 'brand', 'category_site', 'color', 'vendor', ]
    inlines = [SizeAttributeInline, CharacteristicsInline, ImageInline,]
    actions = [site_active, non_site_active, is_featured_action, is_not_featured_action ]
    fieldsets = (
        ('Γενικά Στοιχεία', {
            'fields':(('active', 'site_active', 'is_featured'),
                      ('is_service', 'wholesale_active'),
                      ('title', 'color', 'tag_final_price'),
                      )
        }),
        ('Αποθήκη', {
            'fields': (
                ('order_code', 'vendor', 'category',),
                ('qty', 'qty_kilo', 'measure_unit'),
                ('barcode', 'notes', 'safe_stock'),
                'size',
            )
        }),
        ('Pricing', {
            'fields':(('price', 'price_discount'),
                      ('price_buy', 'order_discount'),
                      ('margin', 'markup', 'price_internet', 'price_b2b'),
                      )
        }),
        ('Site',{
            'fields':(('sku', 'status'), 
                    ('category_site', 'brand'), 
                    ('site_text'),
                    ('slug', 'meta_description'),
                    ('related_products', 'different_color',)
                
                )
        }),
    )
    '''
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "related_products":
            kwargs["queryset"] = Product.objects.filter(category__id__in=self.instance.pk)
        return super(ProductAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    '''
        

class SupplyAdmin(ImportExportModelAdmin):
    search_fields = ['title', 'phone', 'phone1', 'fax', 'email', 'site', 'afm' ]
    list_display = ['title','balance', 'phone', 'phone1', 'fax', 'email', 'site', 'doy', 'afm',]
    list_filter = ['doy',]
    fieldsets = (
        ('Στοιχεία',{
            'fields':('title',('phone','phone1','fax'),('email','site'),'address','description')
        }),
        ('Οικονομικά Στοιχεία',{
            'classes':('collapse',),
            'fields':(('doy','afm'),'balance', 'remaining_deposit')
        }),

    )


class PhotoAdmin(admin.ModelAdmin):
    list_display = ['image_tag_tiny', 'title', 'active', 'is_primary', 'is_back']
    list_filter = ['product', 'active', 'is_primary', 'is_back']
    readonly_fields = ['image_tag']
    fields = ['active','image_tag', 'image', 'product', 'title', 'is_primary', 'is_back', 'alt']


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductPhotos, PhotoAdmin)
admin.site.register(ProductCharacteristics, ProductCharacteristicAdmin)
admin.site.register(Vendor, SupplyAdmin)

admin.site.register(SameColorProducts)
admin.site.register(Color, DraggableMPTTAdmin)
admin.site.register(Size, DraggableMPTTAdmin)

admin.site.register(Characteristics)
admin.site.register(CharacteristicsValue)
admin.site.register(RelatedProducts)
