import kernel.journaling as Journaling
import kernel.partitionmgr as PartitionManager

import json
import hashlib

def authorize(capability: str, authorizationMethod: str, username: str, data: str, encodeDataToSHA256: bool = True) -> bool:
    # Create directory if not exist
    PartitionManager.Etc.mkdir("authorization")

    Journaling.record("INFO", f"Authorization requested for {username} with capability {capability} and method {authorizationMethod}")

    # Load the authorization file
    if not PartitionManager.Etc.isFile("authorization/data"):
        Journaling.record("WARNING", "Authorization data not found. Creating new one.")
        PartitionManager.Etc.copyDefault("authorization/data")
        Journaling.record("INFO", "Authorization data created from defaults.")
    else:
        Journaling.record("INFO", "Authorization data available.")

    # Parse the JSON
    rawStr = PartitionManager.Etc.read("authorization/data")
    authData = json.loads(rawStr)

    # Check if the user is authorized
    logins = authData["logins"]
    accountObject = None

    # Search for the account object
    for accountObj in logins:
        if accountObj["username"] == username:
            accountObject = accountObj
            break

    if accountObject is None:
        Journaling.record("WARNING", f"Account {username} not found.")
        return False

    # Check if the account is enabled
    if not accountObject["capability"][capability] or not accountObject["capability"]["enabled"]:
        Journaling.record("WARNING", f"Account {username} is not enabled or does not have capability {capability}. (enabled: {accountObject['capability']['enabled']}, capability: {accountObject['capability'][capability]})")
        return False

    # Check if the account has the authorization method
    for auth in accountObject["authentications"]:
        if auth["type"] == "free":
            Journaling.record("INFO", f"Account {username} has free access: Authorization granted.")
            return True
        elif auth["type"] == authorizationMethod:
            if encodeDataToSHA256:
                data = hashlib.sha256(data.encode()).hexdigest()
            Journaling.record("INFO", f"Account {username} has authorization method {authorizationMethod}: Checking data - {auth['data']} == {data}")
            return auth["data"] == data

    return False


