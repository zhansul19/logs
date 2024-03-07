from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from database import get_db
from auth import get_current_user
from sqlalchemy.orm import Session
from routes.itab import search_log
import asyncio

# Mocking get_db and get_current_user dependencies
def mock_get_db():
    return MagicMock(spec=Session)

def mock_get_current_user():
    return "test_user"

app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user

# Mocking the database query
@patch('database.User')
@patch('database.Log')
async def test_search_log(mock_Log, mock_User):
    # Mocking the return value of the database query
    mock_query = MagicMock()
    mock_query.join().order_by().all.return_value = [
        ("user1", "user1@example.com", "request_body", "request_rels", "2024-03-06", "approvement_data", "obwii", "depth_", "limit_")
    ]
    mock_db = MagicMock()
    mock_db.query.return_value = mock_query

    # Call the handler function
    response = await search_log(db=mock_db)

    # Assert the response
    assert response == [{
        'username': "user1",
        'email': "user1@example.com",
        'request_body': "request_body",
        'request_rels': "request_rels",
        'date': "2024-03-06",
        'approvement_data': "approvement_data",
        'obwii': "obwii",
        'depth_': "depth_",
        'limit_': "limit_"
    }]

# Run the test
if __name__ == '__main__':
    asyncio.run(test_search_log())

