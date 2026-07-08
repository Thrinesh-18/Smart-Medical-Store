from locust import HttpUser, between, task


class SearchUser(HttpUser):
    wait_time = between(1, 2)

    @task(4)
    def search(self):
        self.client.post("/search", json={"query": "fever medicine", "top_k": 10, "use_hybrid": True})

    @task(1)
    def autocomplete(self):
        self.client.get("/autocomplete", params={"q": "para"})
