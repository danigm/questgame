# QuestGame

A game Engine built on Python and Pygame, created by [danigm](http://danigm.net).

## Install

To get it running you just need the **pygame** library.

* apt-get install python-pygame (or the equivalent in your GNU/Linux distribution)

## Example

You can run the example with:

* python game.py [options]

where options are...

* -n Select the name of the main character
* -s IP:PORT
* -p Select the image of the main character

if you wanted to connect client and server you should do

* python server.py -p 8899
* python game.py -s localhost:8899

Have fun! :-)
