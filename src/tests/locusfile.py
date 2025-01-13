from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 5)

    @task
    def upload_image(self):
        with open("test_image.jpg", "rb") as image_file:
            self.client.post("/upload", files={"image": image_file})

    @task
    def check_status(self):
        self.client.get("/status?file_name=test_image.jpg")

    @task
    def download_image(self):
        self.client.get("/download?file_name=compressed_test_image.jpg")

