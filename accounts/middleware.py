from django_user_agents.utils import get_user_agent


class UserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user.user_agent = get_user_agent(request)
            request.user.save()

        return self.get_response(request)
