from phue import Bridge
import time
import argparse


def get_active_groups(state):
    # select only rooms, ignoring zones
    groups = state["groups"]
    groups = {k: v for k, v in groups.items() if v["type"] == "Room"}

    # select active groups
    return {id: group for id, group in groups.items() if group["state"]["any_on"]}


def get_room_brightnesses(state):
    return {k: v["action"]["bri"] for k, v in state["groups"].items()}


def get_tradfri_lights(state, room):
    room_lights = {light_id: state["lights"][light_id] for light_id in room["lights"]}
    return {k: light for k, light in room_lights.items() if light["manufacturername"] == "IKEA of Sweden"}


previous_room_brightnesses = {}
def fix_brightness(state):
    global previous_room_brightnesses

    current_room_brightnesses = get_room_brightnesses(state)
    if previous_room_brightnesses != current_room_brightnesses:
        for group in get_active_groups(state).values():
            group_brightness = group["action"]["bri"]

            tridfri_lights = get_tradfri_lights(state, group)
            for x in range(0, 3):  # run multiple times to allow for animations to complete
                for light_id in tridfri_lights.keys():
                    light_id = int(light_id)
                    b.set_light(light_id, "bri", group_brightness)

                time.sleep(.5)

    previous_room_brightnesses = current_room_brightnesses


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trådfri bulb brightness fixer")
    parser.add_argument("bridge_ip", help="The IP address of your Philips Hue bridge")
    args = parser.parse_args()

    b = Bridge(args.bridge_ip)
    b.connect()

    while True:
        state = b.get_api()
        fix_brightness(state)
        time.sleep(1)
