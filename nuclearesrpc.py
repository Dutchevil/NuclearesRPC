import psutil
import time
import sys
import requests
import pypresence
import subprocess
from typing import Dict


VARIABLE_TYPES = {
    "CORE_TEMP": float,
    "GENERATOR_0_KW": float,
    "GENERATOR_1_KW": float,
    "GENERATOR_2_KW": float,
    "CORE_IMMINENT_FUSION": str,
    "RODS_POS_ORDERED": float
}


def get_all_vars(srv_url: str) -> Dict[str, float | str]:
    """
    Request a list of dvars from the webserver
    :param srv_url: URL to the webserver, typically localhost:8785
    :return: A dictionary of cast variables and their names
    :rtype: Dict[str, float | str]
    """
    results = {}
    for key, typeof in VARIABLE_TYPES.items():
        res = requests.get(
            srv_url,
            {
                "Variable": key
            }
        )
        results[key] = typeof(res.text)
    return results


def find_nucleares() -> psutil.Process | None:
    """
    Find the running Nucleares.exe process, if it exists
    :rtype: psutil.Process
    :return: A psutil Process representing Nucleares
    """
    for process in psutil.process_iter():
        if process.name() == "Nucleares.exe":
            return process
    return None


if len(sys.argv) > 1:
    if sys.argv[1].endswith("Nucleares.exe"):
        # Client is launching through steam, we are expected to launch it on Steam's behalf
        game_exec = subprocess.Popen(sys.argv[1])


cid = 1331101603649818786
presence = pypresence.Presence(cid, pipe=0)
print("Locating running Nucleares executable...")
proc = find_nucleares()
while proc is None:
    proc = find_nucleares()
    time.sleep(5)
print("Found: " + str(proc.pid))
starttime = time.time()


print("Looking for webserver...")
port = "8785"
url = "http://localhost:" + port + "/"
while 1:
    try:
        # Try to query data until it succeeds
        requests.get(url, {"Variable": "CORE_TEMP"})
        break
    except requests.ConnectionError as e:
        time.sleep(5)
print("Webserver is live, firing up RPC...")


mission = False
presence.connect()
print("Connected. Press Ctrl+C to Exit")
while 1:
    try:
        dvars = get_all_vars(url)
        if dvars["CORE_TEMP"] <= 50:
            details = "Reactor Offline"
        else:
            details = f"Reactor Online: {round(dvars['CORE_TEMP'])}C"
        pwr = round(dvars["GENERATOR_0_KW"] + dvars["GENERATOR_1_KW"] + dvars["GENERATOR_2_KW"])
        if pwr > 0:
            status = f"Producing {pwr} kW"
        else:
            status = "Generator Offline"
        if dvars["CORE_IMMINENT_FUSION"] == "TRUE":
            details = "Imminent Meltdown"
        if (dvars["CORE_TEMP"] == 20 and dvars["RODS_POS_ORDERED"] == 87.5) or mission:
            # I can give you my complete assurance that my work will be back to normal~
            mission = True
            details = "This mission is too important"
            status = "The intruder must be dealt with"
        presence.update(
            pid=proc.pid,
            start=round(starttime),
            details=details,
            state=status,
            large_image="nucleares"
        )
        #print(
        #    f"Sent Update: Core = {dvars['CORE_TEMP']} - Total Pwr = {pwr} - Panic = {dvars['CORE_IMMINENT_FUSION']}",
        #    f"- Rods: {dvars['RODS_POS_ORDERED']}"
        #)
        time.sleep(15)
    except requests.ConnectionError:
        print("Webserver connection lost, trying to re-establish...")
        if find_nucleares() is None:
            print("Nucleares is closed, RPC will close...")
            presence.close()
            sys.exit(0)
        while 1:
            try:
                # Try to query data until it succeeds
                requests.get(url, {"Variable": "CORE_TEMP"})
                break
            except requests.ConnectionError as e:
                time.sleep(5)
            print("Connected!")
            continue
