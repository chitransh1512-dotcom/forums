from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseForbidden
from .models import Post,Thread,Report,Tag
from django.contrib.auth.decorators import permission_required,login_required,user_passes_test
from django import forms
from django.core.paginator import Paginator
from django_ratelimit.decorators import ratelimit
from rapidfuzz import fuzz
from django.db.models import Q
# Create your views here.

# Forms
class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = [
            "category",
            "title",
            "content",
            "courses",
            "resources",
            "tags",
        ]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason"]

# Helpers

def is_trusted_user(user):
    return user.is_superuser or user.has_perm("forum.change_thread")

# Thread views

@login_required
def thread_list(request):
    thread_qs = Thread.objects.all().order_by("-created_at")
    paginator = Paginator(thread_qs, 13)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "forum/thread_list.html",
        {"page_obj": page_obj}
    )

@login_required
def search_threads(request):
    query = request.GET.get("q", "").strip()
    threads = []

    if query:
        tokens = query.lower().split()

        q_filter = Q()
        for token in tokens:
            q_filter |= Q(title__icontains=token)
            q_filter |= Q(content__icontains=token)

        candidates = Thread.objects.filter(q_filter).distinct()

        content_threads = {}

        for thread in candidates:
            title_score = fuzz.token_set_ratio(query, thread.title)
            content_score = fuzz.token_set_ratio(query, thread.content[:500])
            score = max(title_score * 1.3, content_score)

            if score >= 60:
                content_threads[thread.id] = (score, thread)

        for tag in Tag.objects.all():
            if fuzz.token_set_ratio(query, tag.name) >= 70:
                for thread in tag.threads.all():
                    if thread.id not in content_threads:
                        content_threads[thread.id] = (65, thread)

        threads = sorted(
            content_threads.values(),
            key=lambda item: item[0],
            reverse=True,
        )

        threads = [thread for score, thread in threads]

    paginator = Paginator(threads, 13)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "forum/search_results.html",
        {
            "query": query,
            "page_obj": page_obj,
        }
    )

@login_required
def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    posts = thread.posts.all().order_by("-created_at")

    return render(
        request,
        "forum/thread_detail.html",
        {"thread": thread, "posts": posts},
    )

@login_required
def thread_create(request):
    if request.method == "POST" and not is_trusted_user(request.user):
        limited = ratelimit(
            key="user",
            rate="3/h",
            method="POST",
            block=False,
        )(lambda r: None)(request)

        if limited:
            return render(
                request,
                "forum/rate_limited.html",
                {
                    "action": "creating threads",
                    "retry_after": "1 hour",
                },
                status=429,
            )

    if request.method == "POST":
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.creator = request.user
            thread.save()
            form.save_m2m()
            return redirect("thread_detail", thread.id)
    else:
        form = ThreadForm()

    return render(request, "forum/thread_form.html", {"form": form})

@login_required
def threads_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = Thread.objects.filter(tags=tag).order_by("-created_at")
    paginator = Paginator(qs, 13)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "forum/thread_list.html",
        {
            "page_obj": page_obj,
            "active_tag": tag,
        },
    )

def filter_by_tags(request):
    tag_ids = request.GET.getlist("tags")

    threads = Thread.objects.none()
    selected_tags = Tag.objects.filter(id__in=tag_ids)

    if tag_ids:
        threads = Thread.objects.filter(
            tags__id__in=tag_ids
        ).distinct().order_by("-created_at")

    paginator = Paginator(threads, 13)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "forum/tag_filter.html",
        {
            "tags": Tag.objects.all(),
            "selected_tags": selected_tags,
            "page_obj": page_obj,
        }
    )

@login_required
def like_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    if thread.is_locked:
        return HttpResponseForbidden("Thread is locked")
    if request.user in thread.likes.all():
        thread.likes.remove(request.user)
    else:
        thread.likes.add(request.user)
    return redirect("thread_detail", thread_id=thread.id)

@login_required
@permission_required("forum.change_thread", raise_exception=True)
def toggle_lock_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.is_locked = not thread.is_locked
    thread.save()
    return redirect("thread_detail", thread.id)

# Post views

@login_required
def post_create(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if thread.is_locked:
        return HttpResponseForbidden("Thread is locked")

    if request.method == "POST" and not is_trusted_user(request.user):
        limited = ratelimit(
            key="user",
            rate="10/m",
            method="POST",
            block=False,
        )(lambda r: None)(request)

        if limited:
            return render(
                request,
                "forum/rate_limited.html",
                {
                    "action": "creating posts",
                    "retry_after": "1 minute",
                },
                status=429,
            )

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect("thread_detail", thread.id)
    else:
        form = PostForm()
    return render(request, "forum/post_form.html", {"form": form})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.is_deleted:
        return HttpResponseForbidden("Post deleted")
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect("thread_detail", post.thread.id)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.thread.is_locked:
        return HttpResponseForbidden("Thread is locked")
    if request.user == post.author or request.user.has_perm("forum.delete_post"):
        thread_id = post.thread.id
        post.is_deleted = True
        post.save()
        return redirect("thread_detail", thread_id)

    return HttpResponseForbidden("You are not allowed to delete this post")

# Reporting & moderation

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.is_deleted:
        return HttpResponseForbidden("Post deleted")
    if post.thread.is_locked:
        return HttpResponseForbidden("Thread is locked")

    if request.method == "POST" and not is_trusted_user(request.user):
        limited = ratelimit(
            key="user",
            rate="5/h",
            method="POST",
            block=False,
        )(lambda r: None)(request)

        if limited:
            return render(
                request,
                "forum/rate_limited.html",
                {
                    "action": "reporting posts",
                    "retry_after": "1 hour",
                },
                status=429,
            )

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reported_by = request.user
            report.save()
            return redirect("thread_detail", post.thread.id)
    else:
        form = ReportForm()

    return render(request, "forum/report_post.html", {"form": form})

@login_required
@permission_required("forum.delete_post", raise_exception=True)
def moderate(request):
    reports = Report.objects.filter(resolved=False)
    return render(request, "forum/moderate.html", {"reports": reports})


@login_required
@permission_required("forum.delete_post", raise_exception=True)
def resolve_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    report.resolved = True
    report.save()
    return redirect("moderate")



