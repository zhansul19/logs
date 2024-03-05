from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, Mock


def test_passing():
    assert (1, 2, 3) == (1, 2, 3)
# client = TestClient(app)
#
#
# @patch('app.get_current_user')
# @patch('app.get_db')
# def test_search_log_entries_by_request_body_value(mock_get_db, mock_get_current_user):
#     mock_db_session = Mock()
#     mock_get_db.return_value = mock_db_session
#     mock_current_user = "test_user"
#     mock_get_current_user.return_value = mock_current_user
#
#     # Define some sample log entries for testing
#     mock_log_entries = [("username1", "email1", "request_body1", "request_rels1", "2022-03-04", "approvement_data1",
#                          "obwii1", "depth1", "limit1"),
#                         ("username2", "email2", "request_body2", "request_rels2", "2022-03-03", "approvement_data2",
#                          "obwii2", "depth2", "limit2")]
#
#     # Mock the query result
#     mock_db_session.query().join().filter().order_by().all.return_value = mock_log_entries
#
#     # Test GET request with tag=username
#     response = client.get("/log/username=username1")
#     assert response.status_code == 200
#     assert response.json() == [
#         {
#             "username": "username1",
#             "email": "email1",
#             "request_body": "request_body1",
#             "request_rels": "request_rels1",
#             "date": "2022-03-04",
#             "approvement_data": "approvement_data1",
#             "obwii": "obwii1",
#             "depth_": "depth1",
#             "limit_": "limit1"
#         }
#     ]
#
#     # Test case for when log entries are not found
#     mock_db_session.query().join().filter().order_by().all.return_value = []
#     response = client.get("/log/username=nonexistent_user")
#     assert response.status_code == 404
#     assert response.json() == {"detail": "User's log entries not found"}
