from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return self.user.email

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Resource(models.Model):
    RESOURCE_TYPES = [
        ("PDF", "PDF"),
        ("VIDEO", "Video"),
        ("LINK", "Link"),
    ]
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="resources"
    )
    title = models.CharField(max_length=600)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    link = models.URLField()

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

        self.slug = slug

        super().save(*args, **kwargs)


    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(self.name)
                slug = base_slug
                counter = 1

                while Category.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

            self.slug = slug

            super().save(*args, **kwargs)

    def __str__(self):
        return f"#{self.name}"

class Thread(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="threads"
    )
    courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="threads"
    )
    resources = models.ManyToManyField(
        Resource,
        blank=True,
        related_name="threads"
    )
    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="liked_threads"
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank = False)
    creator = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="threads"
)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name="threads")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["-created_at"]
    
class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="liked_posts"
    )

    def __str__(self):
        return f"Post by {self.author.email}"
    
    class Meta:
        ordering = ["-created_at"]

class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, full_name=instance.get_full_name())
