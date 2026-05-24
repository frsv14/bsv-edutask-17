import pytest
from src.util.dao import DAO
from pymongo.errors import WriteError, DuplicateKeyError
from unittest.mock import patch

import os

@pytest.fixture
def test_dao():
    mock_jsonSchema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["firstName", "lastName", "email"],
            "additionalProperties": False,
            "properties": {
                "_id": {
                    "bsonType": "objectId"
                },
                "firstName": {
                    "bsonType": "string",
                    "description": "the first name of a user must be determined"
                }, 
                "lastName": {
                    "bsonType": "string",
                    "description": "the last name of a user must be determined"
                },
                "email": {
                    "bsonType": "string",
                    "description": "the email address of a user must be determined",
                },
                "done": {
                    "bsonType": "bool"
                }
            }
        }
    }
    with patch('src.util.validators.getValidator', return_value=mock_jsonSchema):
        os.environ["MONGO_URL"] = "mongodb://root:root@localhost:27017"
    
        dao = DAO('user')

        dao.collection.drop()
        dao.collection.database.create_collection('user', validator=mock_jsonSchema)
        dao.collection.create_index([('email', 1)], unique=True)
        yield dao
        dao.collection.delete_many({})

#Tests
@pytest.mark.integration
def test_valid_data(test_dao):
    test_data = {'firstName': 'John', 'lastName': 'Doe', 'email': 'JohnDoe@bth.student.se'}
    test_data_optional = {'firstName': 'Jane', 'lastName': 'Doe', 'email': 'JaneDoe@bth.student.se', 'done': True}

    res = test_dao.create(test_data)
    res2 = test_dao.create(test_data_optional)

    assert res['firstName'] == 'John'
    assert res['lastName'] == 'Doe'
    assert res['email'] == 'JohnDoe@bth.student.se'

    db_insert1 = test_dao.collection.find_one({'email': 'JohnDoe@bth.student.se'})
    assert db_insert1 != None

    assert res2['firstName'] == 'Jane'
    assert res2['lastName'] == 'Doe'
    assert res2['email'] == 'JaneDoe@bth.student.se'

    db_insert2 = test_dao.collection.find_one({'email': 'JaneDoe@bth.student.se'})
    assert db_insert2 != None

@pytest.mark.integration
@pytest.mark.parametrize('test_data', [{'lastName': 'Doe', 'email': 'JohnDoe@bth.student.se'}, 
                                       {'firstName': 'Jane', 'email': 'JaneDoe@bth.student.se'},
                                       {'firstName': 'John', 'lastName': 'Doe'},
                                       {}])
def test_missing_required_fields(test_dao, test_data):
    with pytest.raises(WriteError):
        test_dao.create(test_data)

@pytest.mark.integration
@pytest.mark.parametrize('test_data', [{'firstName': 1, 'lastName': 'Doe', 'email': 'JohnDoe@bth.student.se'}, 
                                       {'firstName': 'Jane', 'lastName': 1, 'email': 'JaneDoe@bth.student.se'},
                                       {'firstName': 'John', 'lastName': 'Doe', 'email': 1},
                                       {'firstName': 1, 'lastName': 2, 'email': 3}])
def test_wrong_data_type(test_dao, test_data):
    with pytest.raises(WriteError):
        test_dao.create(test_data)

@pytest.mark.integration
def test_uniqueItems(test_dao):
    test_data1 = {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'existing@bth.student.se'
    }

    test_data2 = {
        'firstName': 'Jane',
        'lastName': 'Doe',
        'email': 'existing@bth.student.se'
    }

    test_dao.create(test_data1)
    with pytest.raises(WriteError):
        test_dao.create(test_data2)

    count = test_dao.collection.count_documents({'email': 'existing@bth.student.se'})
    assert count == 1
