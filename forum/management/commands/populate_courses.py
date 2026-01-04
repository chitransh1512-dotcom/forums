from django.core.management.base import BaseCommand
from forum.models import Course, Resource, Category, Tag
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Populate base courses, resources, categories, and tags"

    def handle(self, *args, **kwargs):
        # COURSES & RESOURCES

        courses = [
            {
                "code": "CSF101",
                "title": "Computer Programming",
                "department": "Computer Science",
                "resource_type": "LINK",
                "link": "https://www.geeksforgeeks.org/c/c-pointers/"
            },
            {
                "code": "BITSF111",
                "title": "Thermodynamics",
                "department": "Mechanical Engineering",
                "resource_type": "VIDEO",
                "link": "https://youtu.be/kd_6bwynBj8?si=XIoHenzTH4a9HiMU"
            },
            {
                "code": "M101",
                "title": "Multivariable Calculus",
                "department": "Mathematics",
                "resource_type": "PDF",
                "link": "https://blr1.digitaloceanspaces.com/studyzone/Study-Portal/MATH%20F111/Collated%20Slides/Chapter_16.1-16.4.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=DO00EH7AMECQFMKTZXJN%2F20260101%2Fblr1%2Fs3%2Faws4_request&X-Amz-Date=20260101T195529Z&X-Amz-Expires=10800&X-Amz-SignedHeaders=host&X-Amz-Signature=d40953016dd17b8a49cec608895c3dfa19016dae27a8b5b25997dbc610c447bd"
            },
            {
                "code": "BIOF101",
                "title": "Introduction to Biology",
                "department": "Biology",
                "resource_type": "VIDEO",
                "link": "https://youtu.be/PzY0MWEEE6U?si=KGyQ4Z8tZSpcxUkM"
            },
        ]

        for c in courses:
            course, _ = Course.objects.get_or_create(
                code=c["code"],
                defaults={
                    "title": c["title"],
                    "department": c["department"],
                },
            )

            Resource.objects.get_or_create(
                course=course,
                title=f"{c['title']}  Starter Resource",
                defaults={
                    "resource_type": c["resource_type"],
                    "link": c["link"],
                },
            )
        # CATEGORIES

        categories = [
            "General Queries",
            "Exam Prep",
            "Last-Minute Tips",
            "Projects",
        ]

        for name in categories:
            Category.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name)},
            )
        # TAGS

        tags = [
            "midsem",
            "endsem",
            "quiz",
            "assignment",
            "tut test",
        ]

        for tag in tags:
            Tag.objects.get_or_create(
                name=tag,
                defaults={"slug": slugify(tag)},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Courses, resources, categories, and tags populated successfully"
            )
        )
