from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.contrib import admin
from . import models

from .models import ModelsUser


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password "
            "using <a href=\"../password/\">this form</a>."
        ),
    )

    class Meta(UserChangeForm.Meta):
        model = ModelsUser


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'lastname', 'account_id', 'is_admin', 'is_staff', 'is_active')

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "lastname", "date_of_birth", "phone", "account_id")}),
        ("Permissions", {"fields": ("is_admin", "is_staff", "is_active", "status")}),
    )

    def save_model(self, request, obj, form, change):
        # Если изменяется пароль, обновляем его с помощью set_password()
        if form.cleaned_data.get("password"):
            obj.set_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)


admin.site.register(models.ModelsSatus)
admin.site.register(ModelsUser, CustomUserAdmin)
