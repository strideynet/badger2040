# `badger2040`

The plan is to produce a handy library for producing badges with the badger2040.

I may also include some utilities for working more directly with the badger2040.

## Useful commands

Flashing your badger2040:

```sh
tinygo flash --target=badger2040 ./main.go
```

Opening the tty from the device using screen (it may be a different device):

```sh
screen /dev/tty.usbmodem1101 
```
