from fluent.runtime import FluentBundle, FluentResource


_bundles: dict[str, FluentBundle] = {}


def _load_bundle(locale: str) -> FluentBundle:
    if locale in _bundles:
        return _bundles[locale]

    bundle = FluentBundle([locale])
    try:
        with open(f"locales/{locale}/messages.ftl", encoding="utf-8") as f:
            resource = FluentResource(f.read())
        bundle.add_resource(resource)
    except FileNotFoundError:
        with open("locales/en/messages.ftl", encoding="utf-8") as f:
            resource = FluentResource(f.read())
        bundle.add_resource(resource)

    _bundles[locale] = bundle
    return bundle


def get_translated_text(locale: str, message_id: str, **kwargs: str) -> str:
    bundle = _load_bundle(locale)
    message = bundle.get_message(message_id)
    if not message or not message.value:
        bundle = _load_bundle("en")
        message = bundle.get_message(message_id)
    if not message or not message.value:
        return message_id

    value, _ = bundle.format_pattern(message.value, kwargs)
    return value
