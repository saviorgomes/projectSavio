from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        # Login do usuário ao iniciar o teste
        self.login()
        self.login2()

    def login(self):
        response = self.client.post("/login", {"username": "savio", "password": "savio"})
        assert response.status_code == 200

    def login2(self):
        response = self.client.post("/login", {"username": "teste", "password": "teste"})
        assert response.status_code == 200

    @task
    def create_user(self):
        # Simula a inclusão de um novo usuário
        response = self.client.post("/register", {"username": "usuarioteste", "password": "usuarioteste"})
        assert response.status_code == 200