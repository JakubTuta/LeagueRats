def find_highest_playrate_role(champion_data, champion_key):
    roles = champion_data.get(champion_key, None)

    if not roles:
        return None

    highest_playrate_role = list(roles.keys())[0]
    highest_playrate = 0

    for role, stats in roles.items():
        play_rate = stats.get("playRate", 0)
        if play_rate > highest_playrate:
            highest_playrate = play_rate
            highest_playrate_role = role

    return highest_playrate_role


def get_existing_request_data(data, required_keys=[], optional_keys=[]):
    required_data = {}
    optional_data = {}

    for key in required_keys:
        if key not in data:
            raise Exception(f"Missing required key: {key}")

        required_data[key] = data[key]

    for key in optional_keys:
        if key in data:
            optional_data[key] = data[key]

    return required_data, optional_data
