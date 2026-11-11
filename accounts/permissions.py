from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from .models import Role, RegisteredUser, Authority, Admin, Guest

ROLE_CLASS_MAP = {
    Role.REGISTERED: RegisteredUser,
    Role.AUTHORITY: Authority,
    Role.ADMIN: Admin,
}


def resolve_actor(user):
    """
    Single shared mechanism to resolve any user (or AnonymousUser) to its appropriate actor.
    - If unauthenticated, returns Guest instance.
    - If authenticated, returns instance of appropriate proxy class (Admin, Authority, RegisteredUser).
    """
    if not user or not getattr(user, 'is_authenticated', False):
        return Guest()

    target_class = ROLE_CLASS_MAP.get(getattr(user, 'role', None), RegisteredUser)
    if type(user) is target_class:
        return user

    actor = target_class()
    actor.__dict__.update(user.__dict__)
    return actor


def verify_actor_capability(user, capability: str):
    """
    Used by service classes to verify that the actor has the required capability.
    """
    actor = resolve_actor(user)
    if not actor.has_capability(capability):
        raise PermissionDenied(f'Actor lacks capability: {capability}')
    return actor


class ActorCapabilityMixin:
    """
    Class-based view mixin that enforces a required capability.
    - If unauthenticated and capability is missing -> redirect to login.
    - If authenticated and capability is missing -> raise PermissionDenied (403).
    """

    required_capability = None

    def dispatch(self, request, *args, **kwargs):
        actor = resolve_actor(request.user)
        request.actor = actor

        if self.required_capability:
            if not actor.has_capability(self.required_capability):
                if not request.user.is_authenticated:
                    return redirect_to_login(request.get_full_path())
                raise PermissionDenied('You do not have permission to perform this action.')

        return super().dispatch(request, *args, **kwargs)

