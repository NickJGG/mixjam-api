class BaseController:
    def __init__(self, user):
        self.user = user
    
    async def handle_message(self, message):
        if message["type"] == "request":
            return await self.handle_request(message["data"])
        
        return await self.handle_response(message["data"])

    async def handle_request(self, message):
        pass

    async def handle_response(self, message):
        pass

    def create_message(self, data):
        return {
            "type": "response",
            "data": data
        }
