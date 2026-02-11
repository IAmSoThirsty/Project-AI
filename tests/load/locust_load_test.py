from locust import HttpUser, task, between

class ProjectAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health/live")
