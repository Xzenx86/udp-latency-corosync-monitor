from os import environ
import udp_rtt
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from dotenv import load_dotenv
from json import dumps
from signal import signal, SIGINT
import traceback
from multiprocessing import Process, Queue, Lock

load_dotenv()

def print_json(data):
    json_formatted_str = dumps(data, indent=5)
    print(json_formatted_str)

def print_slack(req, slack_client, message, blocks = None):
    response = SocketModeResponse(envelope_id=req.envelope_id)
    slack_client.send_socket_mode_response(response)
    if blocks == None :
        slack_client.web_client.chat_postMessage(channel=environ.get("SLACK_CHANNEL"), text=message)
    else : 
        slack_client.web_client.chat_postMessage(channel=environ.get("SLACK_CHANNEL"), blocks=blocks, text=message)


def close_port(a=None, b=None):
    udp_client.close_connection()
    exit(0)

def print_readme(req, slack_client):
    readme = "Cannot open readme file"
    with open("slack_readme.md", 'r') as file :
        readme = file.read()
    blocks = [{"type" : "section", "text" : {"type" : "mrkdwn", "text" : readme}}]
    print_slack(req, slack_client, "Process not running, cannot evaluate", blocks=blocks)

def process(slack_client: SocketModeClient, req: SocketModeRequest):

    try :
        if req.payload.get("text") != "" :
            text = req.payload.get("text").split()
            command = text[0]
            args = ""
            if len(text) >= 2 :
                args = text[1:]
            if req.type == "slash_commands" and req.payload.get("command") == "/udp_rtt" :
                # Acknowledge the request anyway
                if command == "start":       
                    if not udp_client.is_alive :
                        try:
                            print_slack(req, slack_client, "Starting process")

                            q: Queue = Queue()  

                            udp_client.open_connection()

                            listen_process = Process(
                                target=udp_client.listen,
                                args=(
                                    n, #Buffer size, default value to 1500
                                    True, #Verbose
                                    "", #Save to file
                                    q, #Queue
                                ),
                            )

                            listen_process.start()
                            udp_client.send(f, n, t, True, q, lock)

                            #Block until listen process has finished
                            listen_process.join()
                            print("Exit code : ")
                            print(listen_process.exitcode)

                            #Closing when finished :
                            listen_process.close()

                            #Reset udp_client internal data
                            udp_client.reset()

                        except Exception as e:
                            print(e)
                    else:
                        print_slack(req, slack_client, "Process already started !")

                elif command == "stop": 
                    if udp_client.is_alive :
                        print_slack(req, slack_client, "Stopping process")
                        #Simulate last packet : 
                        lock.acquire()
                        udp_client.packet_index = int(f * t)
                        lock.release()
                    else :
                        print_slack(req, slack_client, "Process allready stopped !")

                elif command == "alert": 
                    print("Setting alert")
                    if args != "" :
                        if args[0].isnumeric() :
                            udp_client.set_alert(float(args[0])/1000)
                            print_slack(req, slack_client, "Alert set to : " + str(args[0]) + " ms")
                        else :
                            print_slack(req, slack_client, "Please provide a numeric value")
                    else :
                        print_slack(req, slack_client, "Please provide a latency limit value in ms")

                elif req.payload.get("text") == "help":
                    print_readme(req, slack_client)
        else:
            print_slack(req, slack_client, "Usage :")
            print_readme(req, slack_client)
    except Exception as e:
        print_slack(req, slack_client, "Exception : " + str(traceback.format_exc()))
        print(traceback.format_exc())



n = 1500 #Buffer size in server.
t = 10 #Client running time, uint is second.
dyna = True #Whether to use dynamic bandwidth adaption.
ip = "127.0.0.1"
rp = 10002
lp = 10003
f = 1.0 #frequency

# Initialize SocketModeClient with an app-level token + WebClient
slack_client = SocketModeClient(
    # This app-level token will be used only for establishing a connection
    app_token=environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
    # You will be using this WebClient for performing Web API calls in listeners
    web_client=WebClient(token=environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
)

udp_client = udp_rtt.Client(
    remote_ip=ip,
    to_port=rp,
    local_port=lp,
    slack_client=slack_client,
)

lock = Lock()

# Add a new listener to receive messages from Slack
# You can add more listeners like this
slack_client.socket_mode_request_listeners.append(process)
# Establish a WebSocket connection to the Socket Mode servers
slack_client.connect()
# Just not to stop this process    

signal(SIGINT, close_port)

from threading import Event
Event().wait()

print("Closing UDP Socket")
udp_client._udp_socket.close()
    
#Start server : 
#python3 udp_rtt.py -s -b 1024 -n 1500 --ip localhost --lp 10002 --rp 10003 --verbose True --stop False