# from django.contrib import admin
# from users.models import MyUser
# from django.contrib.auth.models import User
# from django.contrib.auth.admin import UserAdmin

# # Register your models here.
# class MyUserInline(admin.StackedInline):
#     model = MyUser
#     can_delete = False
#     verbose_name_plural = 'MyUsers'

# class MyUserAdmin(UserAdmin):
#     inlines = (MyUserInline, )

# admin.site.unregister(User)
# admin.site.register(User, MyUserAdmin)