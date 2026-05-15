from rest_framework.throttling import UserRateThrottle


class AdminOrUserThrottle(UserRateThrottle):

    def allow_request(self, request, view):
        if request.user.is_staff:
            self.scope = "admin"
        else:
            self.scope = "user"
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)