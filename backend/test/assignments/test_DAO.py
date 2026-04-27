import pytest
from src.util.dao import DAO
from pymongo.errors import WriteError

import os

@pytest.fixture
def test_dao():
    os.environ["MONGO_URL"] = "mongodb://root:root@localhost:27017"
    dao = DAO('user')

    dao.collection.delete_many({})
    yield dao
    dao.collection.delete_many({})

#Tests
@pytest.mark.integration
def test_valid_data(test_dao):
    test_data = {'firstName': 'John', 'lastName': 'Doe', 'email': 'JohnDoe@bth.student.se'}

    res = test_dao.create(test_data)

    assert res['firstName'] == 'John'
    assert res['lastName'] == 'Doe'
    assert res['email'] == 'JohnDoe@bth.student.se'

    db_insert = test_dao.collection.find_one({'email': 'JohnDoe@bth.student.se'})
    assert db_insert != None

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

@pytest.mark.integration
def test_extra_field(test_dao):
    test_data = {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'JohnDoe@bth.student.se',
        'extraField': 'Value'
    }

    test_dao.create(test_data)
    res_doc = test_dao.collection.find_one({'email': 'JohnDoe@bth.student.se'})
    assert 'Value' not in res_doc