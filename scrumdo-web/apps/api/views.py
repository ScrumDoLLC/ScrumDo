from django.contrib.auth import authenticate
from api.models import DeveloperApiKey, UserApiKey
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.serializers import Serializer
from django.http import HttpResponse
from tastypie.http import HttpUnauthorized

def login(request, **kwargs):
    # self.method_check(request, allowed=['post'])
    # self.is_authenticated(request)
    # self.throttle_check(request)

    developer_key = request.GET.get('developer_key')
    username = request.GET.get('username')
    password = request.GET.get('password')

    if not developer_key or not username or not password:
        return HttpUnauthorized()

    try:
        dev_key = DeveloperApiKey.objects.get(key=developer_key, approved=True)
    except DeveloperApiKey.DoesNotExist:
        return HttpUnauthorized()

    user = authenticate(username=username, password=password)

    if user:
        try:
            key = UserApiKey.objects.get(user=user, developer_key=dev_key)
        except  UserApiKey.DoesNotExist:
            key = UserApiKey(user=user, developer_key=dev_key)
            key.save()

        # self.log_throttled_access(request)
        serializer = Serializer()
        desired_format = determine_format(request, serializer)
        serialized = serializer.serialize({'key' : key.key}, desired_format)
        return HttpResponse(content=serialized, content_type=build_content_type(desired_format))
    else:
        return HttpUnauthorized()

def is_key_valid(request, **kwargs):
    user_key = request.GET.get('user_key')
    try:
        user_key = UserApiKey.objects.get(key=user_key)
        key_valid = True
    except UserApiKey.DoesNotExist:
        key_valid = False
        # self.log_throttled_access(request)
    serializer = Serializer()
    desired_format = determine_format(request, serializer)
    serialized = serializer.serialize({'valid' : key_valid}, desired_format)
    return HttpResponse(content=serialized, content_type=build_content_type(desired_format))
