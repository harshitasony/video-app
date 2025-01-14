import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db, Base
from app.core.config import settings
from app.models.video import Video


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db and create client
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestLinkSharing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.api_key = settings.API_KEY

    def test_generate_link(self):
        db = TestingSessionLocal()
        video_id = "1234_test"
        file_path = f"store/{video_id}.mp4"
        video = Video(
            id=video_id, title="test.mp4", duration=60, size_mb=10, file_path=file_path
        )
        db.add(video)
        db.commit()
        db.close()

        response = client.post(
            f"/api/v1/generate_link?video_id={video_id}",
            headers={"API-Key": self.api_key},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("link", data)
        self.assertIn("expiry_time", data)

    def test_access_video(self):
        db = TestingSessionLocal()
        video_id = "123_test"
        file_path = f"store/{video_id}.mp4"
        video = Video(
            id=video_id, title="test.mp4", duration=60, size_mb=10, file_path=file_path
        )
        db.add(video)
        db.commit()
        db.close()

        response = client.post(
            f"/api/v1/generate_link?video_id={video_id}",
            headers={"API-Key": self.api_key},
        )
        data = response.json()
        link = data["link"]
        response = client.get(link, headers={"API-Key": self.api_key})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "video/mp4")


if __name__ == "__main__":
    unittest.main()
