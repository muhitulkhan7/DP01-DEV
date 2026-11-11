from .permissions import resolve_actor


def actor_context(request):
    """
    Exposes the resolved actor to all templates.
    """
    actor = getattr(request, 'actor', None)
    if actor is None:
        actor = resolve_actor(getattr(request, 'user', None))
    return {
        'actor': actor,
    }

