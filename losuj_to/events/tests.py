from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection
from events.models import Event, Participant
from datetime import date
import requests

User = get_user_model()


class ParticipantUpdateViewQueryTest(TestCase):

    def setUp(self):
        
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123"
        )

        
        self.event = Event.objects.create(
            event_name="Test Event",
            event_date=date.today(),
            owner=self.owner,
            price_currency="PLN",
            active=True,
            confirmed=False,
            draw_date=None,
        )

        
        self.num_participants = 5
        self.participants_data = []

        for i in range(self.num_participants):
            user = User.objects.create_user(
                email=f"participant{i}@test.com",
                password="testpass123"
            )
            participant = Participant.objects.create(
                user=user,
                event=self.event,
                name=f"Participant {i}",
            )
            self.participants_data.append({
                "email": user.email,
                "name": participant.name,
            })

        # Log in as the owner
        self.client = Client()
        self.client.login(email="owner@test.com", password="testpass123")
        #print(f">>>>client:{self.client.__dict__}")

    def test_participant_update_view_get_query_count(self):
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(f'/events/event_update_participants/{self.event.id}')

        print(f"\n📊 Query count: {len(context)}")
        for i, query in enumerate(context, 1):
            print(f"Query {i}: {query['sql'][:100]}...")
            #print(f"Query {i}: {query['sql']}...")

        # Ensure we have at least the basic queries (event + participants)
        self.assertGreaterEqual(len(context), 2,
            "Too few queries captured — expected at least event + participants")

    def test_participant_update_view_response_data(self):
        response = self.client.get(f'/events/event_update_participants/{self.event.id}')

        self.assertEqual(response.status_code, 200)

        context = response.context

        self.assertIn('event_data', context)
        self.assertIn('participants', context)
        self.assertIn('rows_range', context)

        
        self.assertEqual(context['event_data']['event_name'], "Test Event")
        self.assertEqual(context['event_data']['event_id'], self.event.id)
        self.assertEqual(context['event_data']['event_location'], "")

        
        participants_list = context['participants']
        self.assertEqual(len(participants_list), self.num_participants,
            f"Expected {self.num_participants} participants, got {len(participants_list)}")

        for i, (email, name) in enumerate(participants_list):
            expected_email = f"participant{i}@test.com"
            expected_name = f"Participant {i}"

            self.assertEqual(email, expected_email,
                f"Participant {i} email mismatch")
            self.assertEqual(name, expected_name,
                f"Participant {i} name mismatch")

    def test_confirmed_event_not_allowed(self):
        
        self.event.confirmed = True
        self.event.save()

        response = self.client.get(f'/events/event_update_participants/{self.event.id}')

        self.assertEqual(response.status_code, 405)

    def test_participant_data_structure(self):
     
        response = self.client.get(f'/events/event_update_participants/{self.event.id}')

        participants_list = response.context['participants']

        for participant in participants_list:
            self.assertIsInstance(participant, list)
            self.assertEqual(len(participant), 2,
                "Each participant should have [email, name]")

            email, name = participant
            self.assertIsInstance(email, str)
            self.assertIsInstance(name, str)
            self.assertIn("@", email, "Email should contain @")

    def test_participant_name_as_email_when_no_name_provided(self):
        payload = {
            'participants': "\n".join([f"part{i}@test.com," for i in range(self.num_participants)])
        }

        response = self.client.post(f'/events/event_update_participants/{self.event.id}', data=payload)

        self.assertEqual(response.status_code, 302)
        #response = self.client.get(f'/events/event_update_participants/{self.event.id}')
        #participants = response.context['participants']
        participants = Participant.objects.filter(event_id=self.event.id)
        print(participants)
        for participant in participants:
            email, name = participant.user.email, participant.name
            self.assertEqual(name, email)
            print(participant.name)
            print(participant.user.email)
        

    


if __name__ == '__main__':
    import unittest
    unittest.main()
