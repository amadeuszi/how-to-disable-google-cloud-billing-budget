import base64
import json

import functions_framework
from googleapiclient import discovery

PROJECT_ID = "your-project-id"
PROJECT_NAME = f"projects/{PROJECT_ID}"

THRESHOLD = 0.85


@functions_framework.cloud_event
def stop_billing(cloud_event):
    """Triggered by a Pub/Sub message from a billing budget alert.
    Disables billing for the project when cost reaches the threshold."""
    pubsub_data = base64.b64decode(
        cloud_event.data["message"]["data"]
    ).decode("utf-8")
    pubsub_json = json.loads(pubsub_data)

    cost = pubsub_json["costAmount"]
    budget = pubsub_json["budgetAmount"]

    if cost < budget * THRESHOLD:
        print(f"No action needed. Cost: {cost}, Budget: {budget}")
        return

    billing = discovery.build("cloudbilling", "v1", cache_discovery=False)
    billing_info = (
        billing.projects().getBillingInfo(name=PROJECT_NAME).execute()
    )

    if not billing_info.get("billingEnabled"):
        print("Billing already disabled")
        return

    billing.projects().updateBillingInfo(
        name=PROJECT_NAME,
        body={"billingAccountName": ""},
    ).execute()
    print(f"Billing disabled for {PROJECT_ID}")
