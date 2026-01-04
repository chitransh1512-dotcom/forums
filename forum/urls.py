from django.urls import path
from . import views

urlpatterns = [
    path("", views.thread_list, name="thread_list"),
    path("thread/<int:thread_id>/", views.thread_detail, name="thread_detail"),
    path("thread/create/", views.thread_create, name="thread_create"),
    path("thread/<int:thread_id>/like/", views.like_thread, name="like_thread"),
    path("thread/<int:thread_id>/lock/", views.toggle_lock_thread, name="lock_thread"),
    path("thread/<int:thread_id>/reply/", views.post_create, name="post_create"),

    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("post/<int:post_id>/report/", views.report_post, name="report_post"),
    path("post/<int:post_id>/like/", views.like_post, name="like_post"),

    path("tag/<slug:slug>/", views.threads_by_tag, name="threads_by_tag"),
    path("tags/", views.filter_by_tags, name="filter_by_tags"),

    path("moderate/", views.moderate, name="moderate"),
    path("report/<int:report_id>/resolve/", views.resolve_report, name="resolve_report"),

    path("search/", views.search_threads, name="search_threads"),
]
