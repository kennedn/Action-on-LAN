# Action-on-LAN
Suite of tools that use low level sockets to listen for magic packets and perform an action when detected.

For example this set of tools makes it possible to issue a `shutdown now` command on recieving a magic packet, allowing the same mechanism to both turn on and off a device.

## How to run
Only python3 needs to be installed

This can be achieve in debain linux variants by doing:

```bash
sudo apt install python3.7
```
Once the dependancies have been met the programs can be run as follows:
```bash
chmod 755 *_actioner
./udp_actioner [command]
or
./eth_actioner [command]
or
./unified_actioner [command]
```

The command will then be executed when a magic-packet is detected.

## udp_actioner
udp_actioner will monitor the network for udp port 9 with valid magic packet data

This type of packet is sent by most wake-on-lan tools / programs

The ```port=``` variable can be overwritten in the source code if you are using a non-standard port. 

## eth_actioner
eth_actioner will monitor the network for wake-on-LAN ethernet frames (0x0842).

This type of packet is sent by ethtool on linux.

## unified_actioner

Does checking for both types of wake-on-LAN packets.

## systemd

Included is an Example.service that can be installed on linux systems running systemd under ```/etc/systemd/system/``` you would then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable Example.service
sudo systemctl start Example.service
```
This would allow the monitor to run in the background, autostarting at boot time.

## notes

If the mac address auto detection is not working for you, you could hard code a mac address at the top of the file in any of the actioners. 

Python is cross platform but at least parts of this tool won't work in windows (e.g mac detection).

## thanks

Big thanks to davidlares for the [gist](https://gist.github.com/davidlares/e841c0f9d9b31f3cd8859575d061c467#file-rawsniffer-py) that got me started on this project
