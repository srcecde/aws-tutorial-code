import os


class Config:
    @property
    def AWS_ACCESS_KEY_ID(self):
        return os.environ.get("AWS_ACCESS_KEY_ID", "AKIAQYQ5LM66HKWAOCUI")

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return os.environ.get(
            "AWS_SECRET_ACCESS_KEY", "IaUKNlrcF5A/izfC4B7TSmqR/jzX6dWSFD60aPv6"
        )

    @property
    def HOST(self):
        return os.environ.get("HOST", "v80579pkii.execute-api.us-east-1.amazonaws.com")

    @property
    def ENDPOINT(self):
        return os.environ.get(
            "ENDPOINT", "https://v80579pkii.execute-api.us-east-1.amazonaws.com/v1"
        )
