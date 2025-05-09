from appwrite.client import Client as AppwriteClient
from appwrite.services.health import Health
from sharded.config import Environment
from appwrite.services.databases import Databases
from appwrite.query import Query

class Services:
    def __init__(self):
        """
        `Services` class is used to connect to Sharded Services and perform various operations.
        """
        self.client = AppwriteClient()

        env = Environment().vital(provider="dynamic")
        self.client.set_endpoint("https://nyc.cloud.appwrite.io/v1")
        self.client.set_project("shardedbot")
        self.client.set_key(env["SERVICE_KEY"])

        self.db = Databases(self.client)
        
        self.health_service = Health(self.client)

    def check_health(self):
        """
        Verify the health of the Sharded Services server.

        Raises:
            Exception: If the health check fails.
        """
        try:
            health_status = self.health_service.get()
            return health_status
        except Exception as e:
            raise Exception(f"Failed to get health status: {e}")

    def server_verified(self, server_id: int):
        """
        A function to check if the server is Sharded Verified or not.
        """
        result = self.db.list_documents(
            database_id="servers",
            collection_id="verified",
            queries=[Query.equal("guildid", server_id)],
        )

        print(result)

        if result['total'] > 0:
            documents = result['documents']
            # Process the retrieved documents
            for document in documents:
                print(f"Document ID: {document['$id']}, Data: {document['data']}")
        else:
            print("No documents found matching the criteria.")

        return {
            "verified": result.get("enabled"),
            "name": result.get("name", "Unknown")
        }
