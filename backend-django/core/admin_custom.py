from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAdminSite(AdminSite):
    REPRESENTATIVE_FILTER = {
            'Appointments': ['Appointment'],
    }

    MANAGER_FILTER = {
            'Appointments': ['Appointment', 'Disposition'],
    }

    def get_app_list(self, request):
        def reduce_app_list(passed_dictionary:dict[str, list[str]]):
            filtered_app_list = []
            for app in app_list:
                if app['name'] in passed_dictionary:
                    app['models'] = [model for model in app['models'] if model['object_name'] in passed_dictionary[app['name']]]
                    if app['models']:  # Only add the app if there are models left
                        filtered_app_list.append(app)
            return filtered_app_list
        app_list = super().get_app_list(request)
        # if request.user.is_superuser:
        #     return app_list
        if False:
            pass
        else:
            user_groups = request.user.groups.values_list('name', flat=True)
            if "Manager" in user_groups:
                return reduce_app_list(self.MANAGER_FILTER)
            elif "Representative" in user_groups:
                return reduce_app_list(self.REPRESENTATIVE_FILTER)
            else:
                return app_list