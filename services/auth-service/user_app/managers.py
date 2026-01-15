from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        username,
        full_name,
        phone,
        role,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not full_name:
            raise ValueError("Full name is required")
        if not phone:
            raise ValueError("Phone is required")
        if not role:
            raise ValueError("Role is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        role = role.upper()

        user = self.model(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            role=role,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        username,
        full_name,
        phone,
        password,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            role="ADMIN",
            password=password,
            **extra_fields,
        )
