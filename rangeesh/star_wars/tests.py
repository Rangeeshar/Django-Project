from django.test import TestCase
from django.contrib.auth.models import User
from tastypie.test import ResourceTestCaseMixin
from tastypie.models import ApiKey
import json

# Create your tests here.
class Resourcetest(ResourceTestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        user = User.objects.create_user(
            "api_client_1",
            "myemail@crazymail.com",
            "mypassword",
        )
        user.save()
        api_key = ApiKey.objects.create(
            user=user, key="204db7bcfafb2deb7506b89eb3b9b715b09905c8"
        )
        api_key.save()

    def get_credentials(self):
        return self.create_apikey(
            "api_client_1", "204db7bcfafb2deb7506b89eb3b9b715b09905c8"
        )

    def test_get_detail_unauthenticated(self):
        response = self.api_client.get("/api/v1/peoples/", format="json")
        self.assertHttpUnauthorized(response)

    def test_throttling(self):
        count = 0
        for i in range(1, 115):
            response = self.api_client.get(
                "/api/v1/peoples/",
                data={
                    "username": "api_client_1",
                    "api_key": "204db7bcfafb2deb7506b89eb3b9b715b09905c8",
                    "name": "c-3po",
                    "birth_year": "112BBY",
                },
                format="json",
                authentication=self.get_credentials(),
            )
        self.assertHttpTooManyRequests(response)

    def test_external_limit(self):
        self.uri = "/api/v1/peoples/"
        count = 0
        for i in range(1, 12):
            t_name = "c-3po{}".format(i)
            response = self.api_client.get(
                self.uri,
                data={
                    "username": "api_client_1",
                    "api_key": "204db7bcfafb2deb7506b89eb3b9b715b09905c8",
                    "name": t_name,
                    "birth_year": "112BBY",
                },
                format="json",
            )
        self.assertEqual(response.status_code, 503)
