from tastypie.api import NamespacedApi

from star_wars.api_resources import peopleresource

v1_api = NamespacedApi(api_name="v1", urlconf_namespace="v1_apis")
v1_api.register(peopleresource.PeopleResource())
