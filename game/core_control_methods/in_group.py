from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def user_in_group(request, groups=[]):
    user_groups = None

    if not request.user.is_superuser:
        if request.user.groups.exists():
            user_groups = request.user.groups.all()

        if user_groups is None:
            messages.add_message(request, messages.ERROR, 'Je hebt geen toegang tot de gevraagde pagina!')
            return redirect('game:adminpanel')

        for group in (groups or []):
            if not user_groups.filter(name=group).exists():
                messages.add_message(request, messages.ERROR, 'Je hebt geen toegang tot de gevraagde pagina!')
                return redirect('game:adminpanel')
    return None

def in_group(groups=[]):
    def decorator(orig_func):

        @wraps(orig_func)
        def wrapper(request, *args, **kwargs):
            res = user_in_group(request, groups)
            if res is not None:
                return res
            return orig_func(request, *args, **kwargs)
        return wrapper
    return decorator

def in_group_on_class(groups=[]):
    def decorator(orig_func):

        @wraps(orig_func)
        def wrapper(request, *args, **kwargs):
            res = user_in_group(request.request, groups)
            if res is not None:
                return res
            return orig_func(request, *args, **kwargs)
        return wrapper
    return decorator