# Action-on-LAN
Suite of tools that use low level sockets to listen for magic packets and perform an action when detected.

For example this set of tools makes it possible to turn a computer both off and on with a wake-on-lan packet.

## How to run
python3 needs to be installed, along with the following module:
- arpreq

This can be achieve in debain linux variants by doing:

```bash
sudo apt install python3.7
```
```bash
python3.7 -m pip install arpreq
```
Once the dependancies have been met the programs can be run as follows:
```bash
chmod 755 *_actioner
./udp_actioner [command]
or
./eth_actioner [command]
```
## udp_actioner
udp_actioner will monitor the network for udp port 9 with valid magic packet data

This type of packet is sent by most wake-on-lan tools / programs

The ```port=``` variable can be overwritten in the source code if you are using a non-standard port. 

## eth_actioner
eth_actioner will monitor the network for wake-on-LAN ethernet frames (0x0842).

This type of packet is sent by ethtool on linux.

## systemd

Included is an Example.service that can be installed on linux systems running systemd under ```/etc/systemd/system/``` you would then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable Example.service
sudo systemctl start Example.service
```
This would allow the monitor to run in the background, autostarting at boot time.

## notes

If the mac address auto detection is not working for you, you could hard code a mac address before the ```While True:``` loop in either of the actioners. 

Python is cross platform and this could possibly work on windows...

