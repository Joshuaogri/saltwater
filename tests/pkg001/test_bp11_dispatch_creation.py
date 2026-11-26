import unittest
from unittest.mock import Mock
from uuid import uuid4
from runtime.bp11_dispatch_creation import PostgresDispatchCreationService

class Auth:
    def decide(self,*a,**k):
        return Mock(allowed=True,active_person_id=42)

class Port:
    def __init__(self): self.command=None
    def create_deployment(self,**kw):
        self.command=kw
        return {"deployment_id":uuid4(),"status":"authorised","unit_id":kw["unit_id"],
                "assigned_members":len(kw["membership_ids"]),"event_id":91}

class DispatchCreationServiceTests(unittest.TestCase):
    def test_creation_requires_officer_and_passes_verified_actor(self):
        port=Port(); service=PostgresDispatchCreationService(Auth(),uuid4(),port)
        member=uuid4()
        result=service.create("session",unit_id="SWPS-UNIT-PATROL",incident_id=5,
            membership_ids=[member],objective="Respond",priority=2,authority_ref="AUTH:1",
            source_ref="CAD:5",idempotency_key="create:5",effective_tick=10)
        self.assertEqual(result["status"],"authorised")
        self.assertEqual(port.command["actor_ref"],"officer-person:42")
    def test_invalid_or_empty_crew_is_rejected(self):
        service=PostgresDispatchCreationService(Auth(),uuid4(),Port())
        with self.assertRaises(ValueError):
            service.create("session",unit_id="u",incident_id=1,membership_ids=[],
                objective="Respond",priority=2,authority_ref="a",source_ref="s",
                idempotency_key="k",effective_tick=0)

if __name__=="__main__": unittest.main()
