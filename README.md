# Action-on-LAN
Run of the mill Wake-on-LAN is a technology that lets network cards power on devices when they recieve a specifically crafted packet (a magic packet).

This repo contains a script that utilises raw sockets to listen for these magic packets whilst powered on and performs a user defined command when detected.

For example this set of tools makes it possible to issue a `shutdown now` command on recieving a magic packet. This means (assuming Wake-On-LAN is enabled) a given magic packet can now toggle the power state of the host.

## How to run
python3 is required to run the script

This can be achieve in debain linux variants by doing:

```bash
sudo apt install python3
```
Once the dependancies have been met the programs can be run as follows:
```bash
chmod 755 magic_actioner.py
sudo ./magic_actioner.py [command]
```

The command will then be executed when a magic-packet is detected. sudo is required to work with raw sockets.

## Functionality
magic_actioner.py will monitor the network for magic packets, both UDP (on configured port) and WOL ethernet frames (0x0842)

`port = 9` can be overwritten in the source code if you are using a non-standard port. 

magic_actioner.py tries to deduce your active mac address. 
`mac_address = None` can be overwritten in the source code to hard code a desired value if auto detection is not working.

## systemd

Included is an Example.service that can be installed on linux systems running systemd under ```/etc/systemd/system/``` you would then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable Example.service
sudo systemctl start Example.service
```
This would allow the monitor to run in the background, autostarting at boot time.

## notes


Python *is* cross platform but at least parts of this tool won't work in windows (e.g mac detection).

## thanks

Big thanks to davidlares for the [gist](https://gist.github.com/davidlares/e841c0f9d9b31f3cd8859575d061c467#file-rawsniffer-py) that got me started on this project
