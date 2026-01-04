from django.contrib import admin

# Register your models here.
from .models import Thread, Post, Report, Course, Resource,Category,Tag

admin.site.register(Post)
admin.site.register(Report)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(Category)
admin.site.register(Tag)

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    fields = (
        "category",
        "title",
        "content",
        "courses",
        "resources",
        "tags",
        "creator",
        "is_locked",
    )
    filter_horizontal = ("courses", "resources","tags")