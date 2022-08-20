package main

import (
	"fmt"
	"image/color"
	"log"
	"machine"
	"time"

	"tinygo.org/x/drivers/uc8151"
	"tinygo.org/x/tinydraw"
	"tinygo.org/x/tinyfont"
	"tinygo.org/x/tinyfont/freemono"
)

// https://cdn.shopify.com/s/files/1/0174/1800/files/badger_2040_schematic.pdf?v=1645702148
var (
	black       = color.RGBA{1, 1, 1, 255}
	white       = color.RGBA{0, 0, 0, 255}
	w     int16 = 296
	h     int16 = 128
)

type Device struct {
	ActLED  machine.Pin
	ABtn    machine.Pin
	BBtn    machine.Pin
	CBtn    machine.Pin
	UpBtn   machine.Pin
	DownBtn machine.Pin

	*uc8151.Device
}

func setupDisplay() (*uc8151.Device, error) {
	err := machine.SPI0.Configure(machine.SPIConfig{
		Frequency: 12000000,
		SCK:       machine.EPD_SCK_PIN,
		SDO:       machine.EPD_SDO_PIN,
	})
	if err != nil {
		return nil, fmt.Errorf("initializing spi0: %w", err)
	}

	display := uc8151.New(
		machine.SPI0,
		machine.EPD_CS_PIN,
		machine.EPD_DC_PIN,
		machine.EPD_RESET_PIN,
		machine.EPD_BUSY_PIN,
	)
	display.Configure(uc8151.Config{
		Rotation: uc8151.ROTATION_270,
		Speed:    uc8151.MEDIUM,
		Blocking: true,
	})

	return &display, nil
}

func setupDevice() (*Device, error) {
	machine.ENABLE_3V3.Configure(machine.PinConfig{Mode: machine.PinOutput})
	machine.ENABLE_3V3.High()

	actLED := machine.LED
	actLED.Configure(machine.PinConfig{Mode: machine.PinOutput})

	aBtn := machine.BUTTON_A
	aBtn.Configure(machine.PinConfig{Mode: machine.PinInput})
	bBtn := machine.BUTTON_B
	bBtn.Configure(machine.PinConfig{Mode: machine.PinInput})
	cBtn := machine.BUTTON_C
	cBtn.Configure(machine.PinConfig{Mode: machine.PinInput})

	upBtn := machine.BUTTON_UP
	upBtn.Configure(machine.PinConfig{Mode: machine.PinInputPulldown})
	err := upBtn.SetInterrupt(machine.PinRising, func(p machine.Pin) {
		actLED.Set(true)
	})
	if err != nil {
		return nil, fmt.Errorf("setting up interrupt: %w", err)
	}
	downBtn := machine.BUTTON_DOWN
	downBtn.Configure(machine.PinConfig{Mode: machine.PinInputPulldown})
	err = downBtn.SetInterrupt(machine.PinRising, func(p machine.Pin) {
		actLED.Set(false)
	})
	if err != nil {
		return nil, fmt.Errorf("setting up interrupt: %w", err)
	}

	display, err := setupDisplay()
	if err != nil {
		return nil, fmt.Errorf("intializing display: %w", err)
	}

	return &Device{
		ABtn:    aBtn,
		BBtn:    bBtn,
		CBtn:    cBtn,
		UpBtn:   upBtn,
		DownBtn: downBtn,

		Device: display,
		ActLED: actLED,
	}, nil
}

func main() {
	device, err := setupDevice()
	if err != nil {
		log.Fatalf("%s\r\n", err)
	}

	if err := run(device); err != nil {
		log.Fatalf("%s\r\n", err)
	}
}

func run(device *Device) error {
	device.ClearBuffer()
	if err := device.Display(); err != nil {
		return err
	}
	if err := AboutMePage(device); err != nil {
		return err
	}
	if err := device.Display(); err != nil {
		return err
	}

	for {
		time.Sleep(500 * time.Millisecond)
		log.Printf("Hello from Badger2040\r\n")
	}
}

func AboutMePage(device *Device) error {
	barHeight := int16(40)
	if err := tinydraw.FilledRectangle(device, 0, 0, w, barHeight, black); err != nil {
		return err
	}

	name := "noah!"
	font := &freemono.Bold18pt7b
	// Center some text!
	// text x, y is bottom left, rather than top left as you might expect
	iw, _ := tinyfont.LineWidth(font, name)
	barTextY := (barHeight / 2) + (18 / 2) // 18 is font height
	barTextX := (w / 2) - (int16(iw) / 2)
	tinyfont.WriteLine(device, font, barTextX, barTextY, name, white)

	return nil
}
