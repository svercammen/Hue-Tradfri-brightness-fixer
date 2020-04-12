import os
import signal
import sys

from phue import Bridge
import time
import argparse


def get_environment_variable(name):
    if name in os.environ:
        return os.environ[name]
    else:
        print(f"Environment variable {name} is not set. Exiting.")
        sys.exit(1)


def get_groups():
    api = b.get_api()

    # get groups; filter lights in group
    groups = {
        int(group_id): [
            int(light_id)
            for light_id
            in group['lights']
            if api['lights'][light_id]["manufacturername"] == "IKEA of Sweden"
        ]
        for (group_id, group)
        in api['groups'].items()
    }

    # filter groups with no lights
    groups = {
        group_id: lights
        for (group_id, lights)
        in groups.items()
        if len(lights) > 0
    }

    return groups


def signal_handler():
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)

    b = Bridge(get_environment_variable("bridge_ip"))
    b.connect()

    groups = get_groups()

    previous_room_brightnesses = {
        group_id: None
        for group_id
        in groups.keys()
    }

    while True:
        for group_id, light_ids in groups.items():
            group = b.get_group(group_id)
            group_brightness = group['action']['bri']

            if previous_room_brightnesses[group_id] != group_brightness:
                previous_room_brightnesses[group_id] = group_brightness

                time.sleep(.5)

                for light_id in light_ids:
                    light = b.get_light(light_id)

                    # if light['state']['bri'] != group_brightness:
                    b.set_light(light_id, "bri", group_brightness)

        time.sleep(.1)
