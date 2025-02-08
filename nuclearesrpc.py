import psutil
import time
import sys
import requests
import pypresence
import subprocess
import argparse
import logging
import traceback
import ctypes
from typing import Dict
import ctypes


__version__ = "v2.0.0"
parser = argparse.ArgumentParser(
    prog="Nucleares Presence Client",
    description="Nucleares Rich Presence Client for Discord",
    epilog=f"Version {__version__}"
)
parser.add_argument("-v", "--version", action="store_true")
parser.add_argument("-d", "--debug", action="store_true")
params = parser.parse_args()
logging.basicConfig(
    level="DEBUG" if params.debug else "INFO",
    filename="debug.log" if params.debug else None
)


if params.version:
    print("Nucleares Rich Presence Client")
    print(f"Client Version: {__version__}")
    print(f"PyPresence Version: {pypresence.__version__}")
    input("Press Enter to exit...")
    sys.exit(0)


VARIABLE_TYPES = {
    "CORE_TEMP": float,
    "GENERATOR_0_KW": float,
    "GENERATOR_1_KW": float,
    "GENERATOR_2_KW": float,
    "CORE_IMMINENT_FUSION": str,
#    "RODS_POS_ORDERED": float
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
        logging.debug(f"Getting key {key}, looking for type {typeof}")
        res = requests.get(
            srv_url,
            {
                "Variable": key
            }
        )
        try:
            hotfix = res.text.replace(",", ".")
            results[key] = typeof(hotfix)
        except ValueError:
            logging.error(f"Conversion of '{res.text}' to type {typeof} failed")
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
    for obj in sys.argv:
        if obj.endswith("Nucleares.exe"):
            # Client is launching through steam, we are expected to launch it on Steam's behalf
            game_exec = subprocess.Popen(obj)

ctypes.windll.user32.MessageBoxW(0, "Remember to turn on the WebServer, else NuclearesRPC will not work!", "Reminder!", 64)
cid = 1331101603649818786
presence = pypresence.Presence(cid, pipe=0)
logging.info("Locating running Nucleares executable...")
proc = find_nucleares()
while proc is None:
    proc = find_nucleares()
    time.sleep(5)
logging.debug("Found: " + str(proc.pid))
starttime = time.time()


logging.info("Waiting for webserver...")
port = "8785"
url = "http://localhost:" + port + "/"
while 1:
    try:
        # Try to query data until it succeeds
        requests.get(url, {"Variable": "CORE_TEMP"})
        break
    except requests.ConnectionError as e:
        time.sleep(5)
logging.info("Webserver is live, firing up RPC...")


mission = False
presence.connect()
logging.info("Connected. Press Ctrl+C to Exit")
while 1:
    try:
        dvars = get_all_vars(url)
        if dvars["CORE_TEMP"] <= 50:
            details = "Reactor Offline"
        else:
            details = f"Reactor Online: {round(dvars['CORE_TEMP'])}\u00B0C"
        pwr = round(dvars["GENERATOR_0_KW"] + dvars["GENERATOR_1_KW"] + dvars["GENERATOR_2_KW"])
        if 0 < pwr < 1000:
            status = f"Producing {pwr} kW"
        elif pwr > 1000:
            status = f"Producing {round(pwr/1000)} mW"
        else:
            status = "Generator Offline"
        if dvars["CORE_IMMINENT_FUSION"] == "TRUE":
            details = "Imminent Meltdown"
        #if (dvars["CORE_TEMP"] == 20 and dvars["RODS_POS_ORDERED"] == 87.5) or mission:
        #    # I can give you my complete assurance that my work will be back to normal~
        #    mission = True
        #    details = "This mission is too important"
        #    status = "The intruder must be dealt with"
        presence.update(
            pid=proc.pid,
            start=round(starttime),
            details=details,
            state=status,
            large_image="nucleares"
        )
        logging.debug(
            f"Sent Update: Core = {dvars['CORE_TEMP']} - Total Pwr = {pwr} - Panic = {dvars['CORE_IMMINENT_FUSION']}",
        #    f"- Rods: {dvars['RODS_POS_ORDERED']}"
        )
        time.sleep(15)
    except requests.ConnectionError:
        logging.warning("Webserver connection lost, trying to re-establish...")
        if find_nucleares() is None:
            logging.info("Nucleares is closed, RPC will close...")
            presence.close()
            sys.exit(0)
        while 1:
            try:
                # Try to query data until it succeeds
                requests.get(url, {"Variable": "CORE_TEMP"})
                break
            except requests.ConnectionError as e:
                time.sleep(5)
            logging.info("Connected!")
            continue

    except Exception as e:
        logging.critical("Client has run into an unexpected error and cannot continue")
        logging.critical("NuclearesRPC has crashed.", exc_info=e)
        logging.critical("Please send this error when asking for support")
        presence.close()
        input("Press Enter to exit...")
        sys.exit(1)
