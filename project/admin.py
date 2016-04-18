from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from project.models import Project


class ProjectAdmin(BaseGroupAdmin):
    filter_horizontal = ('permissions', 'places')

    def delete_model(self, request, obj):
        if obj.name == 'ALL':
            messages.error(
                request,
                'Delete of the group ALL is forbidden')
        else:
            obj.delete()
            return super(ProjectAdmin, self).delete_model(request, obj)

    def get_queryset(self, request):
        """
        Show only projects you managed, except admin user that see all.
        """
        qs = super(ProjectAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(manager=request.user)

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        res = super(ProjectAdmin, self).get_model_perms(request)
        if not request.user.is_superuser:
            is_manager = Project.objects.filter(manager=request.user)
            if not is_manager:
                res = {}
        return res

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('name', 'manager')
        return self.readonly_fields


admin.site.unregister(Group)
admin.site.register(Project, ProjectAdmin)
