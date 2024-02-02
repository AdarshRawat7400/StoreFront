from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class CheckRolesMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role in self.allowed_roles
