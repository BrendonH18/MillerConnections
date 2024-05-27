from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'name', 'phone1', 'phone2', 'street', 'state', 'complete', 'zip', 'created_at')
    list_filter = ('state', 'complete')
    search_fields = ('name', 'phone1', 'phone2', 'street', 'state', 'zip')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('name', 'phone1', 'phone2', 'street', 'state', 'complete', 'zip')
        }),
        ('Important dates', {
            'fields': ('created_at',)
        }),
    )