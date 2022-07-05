from typing import Optional

from pydantic import BaseModel, Field

from short_url.domain.entities import Url


class UrlModel(BaseModel):
    long_url: str = Field(..., alias="longUrl")
    short_url: Optional[str] = Field(..., alias="shortUrl")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    def to_domain(self):
        return Url(long_url=self.long_url, short_url=self.short_url)


class UrlsModel(BaseModel):
    long_url: str = Field(..., alias="longUrl")
    short_urls: list[str] = Field(default_factory=list, alias="shortUrls")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
