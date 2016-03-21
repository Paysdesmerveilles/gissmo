from django.contrib import admin

from document.models import Document, Type


class TypeAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('name',)
    search_fields = ['name']


class DocumentAdmin(admin.ModelAdmin):
    fields = [
        'title',
        '_type',
        'owner',
        '_file',
        'date',
        'start',
        'end',
        'private_link']
    list_display = ('title', '_type', 'owner', 'date')
    list_filter = ['_type']
    search_fields = ['title', 'owner']

admin.site.register(Type, TypeAdmin)
admin.site.register(Document, DocumentAdmin)
