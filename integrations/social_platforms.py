"""Social platform integration status. No account discovery API is connected in this beta."""
def integration_status():
    return {
        "connected": False,
        "verification_capability": False,
        "message": "Manual audit only. No social platform APIs are connected; account status is user-entered and should not be described as independently verified."
    }
