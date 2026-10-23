"""Publishing adapter placeholder with an explicit safe failure."""
class PublishingNotConfigured(RuntimeError):
    pass

def publish_content(content_id):
    raise PublishingNotConfigured(
        "No publishing integration is configured. Content remains in your local calendar; no post was published."
    )
