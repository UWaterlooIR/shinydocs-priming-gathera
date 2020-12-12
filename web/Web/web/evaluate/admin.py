from django.contrib import admin

from web.evaluate.models import Qrel


class NoAddNoDeleteAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Qrel, NoAddNoDeleteAdmin)
