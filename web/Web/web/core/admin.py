from django.contrib import admin

from web.core.models import Session, SharedSession


class NoAddNoDeleteAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Session, NoAddNoDeleteAdmin)
admin.site.register(SharedSession)
