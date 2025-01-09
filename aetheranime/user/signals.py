from social_core.pipeline.partial import partial


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == "google-oauth2":
        user.profile.avatar_url = response.get("picture")
        user.profile.save()
