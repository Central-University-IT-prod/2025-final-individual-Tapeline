class CampaignCreateException(Exception):
    def __init__(self, response: dict):
        super().__init__()
        self.response = response

    def __str__(self):
        return self.beautiful_message()

    def beautiful_message(self) -> str:
        if "profanity" in self.response["detail"].lower():
            return (
                f"Your message contains profanity: "
                f"{self.response['extra']['word']}"
            )
        return self.response['detail']
