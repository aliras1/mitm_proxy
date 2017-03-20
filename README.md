# MITMProxy

This application is a Man-In-The-Middle-Attack tool for learning purpuses only. It poisons the ARP and/or NDP tables of the targeted host and sets up a proxy server between the target and the Default Gateway. This server intercepts both HTTP and HTTPS communication. However by HTTPS the client must accept the applications fake Certificate, of course.

## Overwiew

If the application is running you will see the target's HTTP requests and the POST parameters.

## Install

## Usage

`sudo python3 mitmproxy.py <interface> {-t <target ipv4> | -t6 <target ipv6>}` At least one of -t or -t6 should be there. You can define both as well.

## Known bugs

It does not work quiet well with some HTTPS servers. Currently i'm using the module HTTPSConnection of http.client for communicating with real world HTTPS servers.

## License

Copyright (c) 2017 László Sári. Licensed under the MIT license.
