import os


class Config:
    @property
    def AWS_ACCESS_KEY_ID(self):
        return os.environ.get("AWS_ACCESS_KEY_ID", "")

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return os.environ.get(
            "AWS_SECRET_ACCESS_KEY", ""
        )

    @property
    def HOST(self):
        return os.environ.get("HOST", "")

    @property
    def ENDPOINT(self):
        return os.environ.get(
            "ENDPOINT", ""
        )
