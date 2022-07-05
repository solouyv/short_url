from http import HTTPStatus

from short_url.domain.entities import Urls


class TestUrlAPI:
    def test_create_url__no_url__no_short_url__created(self, client, url):
        res = client.post("/", json={"longUrl": url.long_url, "shortUrl": None})
        json_response = res.json()

        assert res.ok
        assert json_response["longUrl"] == url.long_url
        assert json_response["shortUrl"]

    def test_create_url__no_url__with_short_url__created(self, client, url):
        res = client.post("/", json={"longUrl": url.long_url, "shortUrl": url.short_url})
        json_response = res.json()

        assert res.ok
        assert json_response["longUrl"] == url.long_url
        assert json_response["shortUrl"] == url.short_url

    def test_create_url__url_exists__diff_short_url__created(self, client, url, url_repository):
        res = url_repository().create(url)
        res = client.post("/", json={"longUrl": res.long_url, "shortUrl": "eeeee"})
        json_response = res.json()

        assert res.ok
        assert json_response["longUrl"] == url.long_url
        assert json_response["shortUrl"] == "eeeee"

    def test_create_url__url_exists__same_short_url__already_exists(self, client, url_repository, url):
        res = url_repository().create(url)
        res = client.post("/", json={"longUrl": res.long_url, "shortUrl": res.short_url})

        assert res.ok
        assert "already_exists_error" in str(res.content)

    def test_get_list__no_urls__empty_list(self, client):
        res = client.get("/")

        assert res.ok
        assert res.context["urls"] == []

    def test_get_list__urls_exist__gotten(self, client, url_repository, url):
        for i in range(1, 4):
            url.long_url = f"{url.long_url}{i}/"
            for j in range(1, 4):
                url = url_repository().create(url)
                url.short_url = f"{url.short_url}/{j}"
        res = client.get("/")

        assert res.ok
        assert len(res.context["urls"]) == 3
        assert len(res.context["urls"][0].short_urls) == 3

    def test_get__url_exists__gotten(self, client, url, url_repository):
        res = url_repository().create(url)
        res = client.get(f"/{res.short_url}")

        assert res.ok
        assert res.context["urls"] == [Urls(long_url=url.long_url, short_urls=[url.short_url])]

    def test_get__no_url__not_found(self, client):
        res = client.get("/test")

        assert res.ok
        assert "not_found_error" in str(res.content)

    def test_delete_all__urls_exist__deleted(self, client, url_repository, url):
        for i in range(1, 4):
            url.long_url = f"{url.long_url}{i}/"
            for j in range(1, 4):
                url = url_repository().create(url)
                url.short_url = f"{url.short_url}/{j}"
        assert client.get("/").context["urls"]
        res = client.delete("/")

        assert res.status_code == HTTPStatus.NO_CONTENT
        assert not client.get("/").context["urls"]

    def test_delete_all__no_urls__no_errors(self, client):
        assert not client.get("/").context["urls"]
        res = client.delete("/")

        assert res.status_code == HTTPStatus.NO_CONTENT
