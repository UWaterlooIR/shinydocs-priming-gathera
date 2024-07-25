from django.contrib import admin

from web.core.models import Session, SharedSession, SessionTimer


class NoAddNoDeleteAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Session, NoAddNoDeleteAdmin)
admin.site.register(SharedSession)

@admin.register(SessionTimer)
class SessionTimerAdmin(admin.ModelAdmin):
    list_display = ('session', 'start_time', 'end_time', 'time_spent')
    list_filter = ('session', 'start_time', 'end_time', 'time_spent')
    search_fields = ('session', 'start_time', 'end_time', 'time_spent')
