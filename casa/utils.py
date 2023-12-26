def clean_mac(mac: str) -> str:
    return mac.replace(" ", "_").replace(":", "_")
