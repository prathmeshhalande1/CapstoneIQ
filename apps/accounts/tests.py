from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import GroupMembership, projectGroup, userProfile


class ProjectGroupChatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password')
        self.client.force_login(self.user)

    def test_created_group_appears_in_chat_sidebar(self):
        response = self.client.post(
            reverse('create_group'),
            {'group_name': 'Created Group'},
        )

        self.assertRedirects(response, reverse('home'))
        group = projectGroup.objects.get(groupName='Created Group')
        profile = userProfile.objects.get(user=self.user)
        self.assertTrue(
            GroupMembership.objects.filter(student=profile, group=group).exists()
        )

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Created Group')
        self.assertContains(response, '👥 1')

    def test_joined_group_appears_in_chat_sidebar(self):
        owner = User.objects.create_user(username='owner', password='password')
        group = projectGroup.objects.create(groupName='Joined Group', createdBy=owner)

        response = self.client.post(
            reverse('join_group'),
            {'invite_code': group.groupCode.lower()},
        )

        self.assertRedirects(response, reverse('home'))
        profile = userProfile.objects.get(user=self.user)
        self.assertTrue(
            GroupMembership.objects.filter(student=profile, group=group).exists()
        )

        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Joined Group')
        self.assertContains(response, '👥 1')
