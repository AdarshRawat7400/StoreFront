from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from apps.core.utils import generate_random_password
from apps.users.models import Admin, Users

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):


    

    def pre_social_login(self, request, sociallogin):
            # Access social login details
            provider = sociallogin.account.provider
            uid = sociallogin.account.uid
            extra_data = sociallogin.account.extra_data
            admin = Admin.objects.first()

            user_data = {}

            # Perform custom logic based on the social login details
            if provider == 'google':
                user_data['username'] = f"{provider}-{extra_data.get('sub')}"
                # user_data['email'] = extra_data.get('email')
                user_data['first_name'] = extra_data.get('given_name')
                user_data['last_name'] = extra_data.get('family_name')
                user_data['full_name'] = extra_data.get('name')

            
            user_data['role'] = 'customer'
            user_data['is_active'] = True
            user_data['password'] = generate_random_password()
            user_data['admin'] = admin

            user, created = Users.objects.update_or_create(
                username=user_data['username'],
                defaults=user_data
            )



