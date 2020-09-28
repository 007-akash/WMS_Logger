from luma.core.interface.serial import spi
import luma.core.device as Device
from luma.core.render import canvas

serial = spi(port=0, device=0, gpio_DC=23, gpio_RST=24)
x = Device.device(serial_interface=serial)
x.capabilities(width=128,height=64,rotate=0,mode = "1")
##with canvas(device) as draw:
##    draw.rectangle(device.bounding_box, outline="white", fill="black")
##    draw.text((10, 40), "Hello World", fill="red")

##x.show()
x.command(0x01)
x.command(0x02)
x.command(0x06)
x.command(0x0C)
x.command(0x93)
x.data(0x65)
