from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=160,unique=True)

    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        if self.code:
            self.code = self.code.upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=160,unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=160,unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    email = models.EmailField(unique=True)

    job_title = models.CharField(max_length=150, blank=True)

    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        related_name="users",
        on_delete=models.SET_NULL,
    )

    position = models.ForeignKey(
        Position,
        null=True,
        blank=True,
        related_name="users",
        on_delete=models.SET_NULL,
    )

    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="users",
    )

    phone_number = models.CharField(max_length=50, blank=True)

    def has_role(self, code):
        return self.roles.filter(code=code, is_active=True).exists()

    def __str__(self):
        return self.get_full_name() or self.username