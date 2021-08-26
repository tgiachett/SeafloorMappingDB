# Snapshot testing referenced here: https://docs.graphene-python.org/en/latest/testing/
# https://github.com/syrusakbary/snapshottest/#reasons-to-use-this-package

import json
import pytest
from graphene.test import Client

from smdb.models import MissionType, Person
from smdb.schema import schema

pytestmark = pytest.mark.django_db

create_missiontype_mutation = """mutation {
        create_missiontype(missiontype_name: "Initial") {
            missiontype {
            missiontype_name
            }
        }
    }"""

create_person_mutation = """mutation {
        create_person(first_name: "Jane", last_name: "Doe", institution_name: "MBARI") {
            person {
                first_name
                last_name
                institution_name
            }
        }
    }"""

create_person_mutation_uuid = """mutation {
        create_person(first_name: "Jane", last_name: "Doe", institution_name: "MBARI") {
            person {
                uuid
            }
        }
    }"""


def test_all_missiontypes_empty(snapshot):
    client = Client(schema)
    snapshot.assert_match(
        client.execute(
            """{
                all_missiontypes {
                    missiontype_name
                    uuid
                  }
                }"""
        )
    )


# ===== MissionType Tests =====
def test_create_missiontype(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(create_missiontype_mutation))
    assert MissionType.objects.all()[0].missiontype_name == "Initial"


def test_update_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation)
    assert MissionType.objects.all()[0].missiontype_name == "Initial"

    snapshot.assert_match(
        client.execute(
            """mutation {
                update_missiontype(missiontype_name: "Initial", new_missiontype_name: "Updated") {
                    missiontype {
                    missiontype_name
                    }
                }
            }"""
        )
    )
    assert MissionType.objects.all()[0].missiontype_name == "Updated"


def test_delete_missiontype(snapshot):
    client = Client(schema)
    client.execute(create_missiontype_mutation)
    snapshot.assert_match(
        client.execute(
            """mutation {
                delete_missiontype(missiontype_name: "Initial") {
                    missiontype {
                    missiontype_name
                    }
                }
            }"""
        )
    )
    assert MissionType.objects.all().count() == 0


# ===== Person Tests =====
def test_create_person(snapshot):
    client = Client(schema)
    snapshot.assert_match(client.execute(create_person_mutation))
    assert Person.objects.all()[0].first_name == "Jane"
    assert Person.objects.all()[0].last_name == "Doe"
    assert Person.objects.all()[0].institution_name == "MBARI"


# https://medium.com/@jamesvaresamuel/mutation-and-query-in-graphql-using-python-django-part-2-79d9852a1092
def test_update_person(snapshot):
    client = Client(schema)
    response = client.execute(create_person_mutation_uuid)
    uuid = response["data"]["create_person"]["person"]["uuid"]

    snapshot.assert_match(
        client.execute(
            """mutation UpdatePerson($uuid: String!) {
            update_person(uuid: $uuid, first_name: "Jim", last_name: "Roe", institution_name: "SIO") {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variables={"uuid": uuid},
        )
    )
    assert Person.objects.all()[0].first_name == "Jim"
    assert Person.objects.all()[0].last_name == "Roe"
    assert Person.objects.all()[0].institution_name == "SIO"


def test_delete_person(snapshot):
    client = Client(schema)
    response = client.execute(create_person_mutation_uuid)
    uuid = response["data"]["create_person"]["person"]["uuid"]
    snapshot.assert_match(
        client.execute(
            """mutation DeletePerson($uuid: String!) {
            delete_person(uuid: $uuid) {
                person {
                    first_name
                    last_name
                    institution_name
                }
            }
        }""",
            variables={"uuid": uuid},
        )
    )
    assert Person.objects.all().count() == 0
