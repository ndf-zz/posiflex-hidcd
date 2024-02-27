# posiflex-hidcd

Example interface for Posiflex USB HID Cash Drawer

## Usage

	from hidcd import HidCd
	cd = HidCd(7)  # use cash drawer with id=7
	if cd.closed():
	    cd.open()

On linux, read/write access to the /dev/hidrawX device
file may be required. See example udev rule 99-posiflex.rule
for a possible approach.

## Device Info

Tested with Posiflex CR-4115G2/CR-4000 Series:

	ID 0d3a:020X Posiflex Technologies, Inc. Series 3xxx Cash Drawer

HID Descriptor:

	0x06, 0xA0, 0xFF,  // Usage Page (Vendor Defined 0xFFA0)
	0x09, 0x01,        // Usage (0x01)
	0xA1, 0x01,        // Collection (Application)
	0x09, 0x02,        //   Usage (0x02)
	0x15, 0x00,        //   Logical Minimum (0)
	0x26, 0xFF, 0x00,  //   Logical Maximum (255)
	0x75, 0x08,        //   Report Size (8)
	0x95, 0x78,        //   Report Count (120)
	0x81, 0x02,        //   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
	0x09, 0x03,        //   Usage (0x03)
	0x15, 0x00,        //   Logical Minimum (0)
	0x26, 0xFF, 0x00,  //   Logical Maximum (255)
	0x75, 0x08,        //   Report Size (8)
	0x95, 0x78,        //   Report Count (120)
	0x91, 0x02,        //   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
	0xC0,              // End Collection
 
## Protocol

Command (120 bytes, host to device):

	[CDNUM] [COMMAND] 0x00 ... 0x00

   - [CDNUM] is the drawer number (0-7)
   - [COMMAND] is one of:
      - CDNUM: Open drawer
      - CDNUM+1: Drawer status

Status (120 bytes, device to host):

	[STATUS] 0x?? ... 0x??

   - STATUS is (CDNUM<<4)|CLOSED:
      - CLOSED==0: Drawer is open
      - CLOSED==1: Drawer is closed

## Notes

   - Open command is the drawer number
   - Status command is drawer number plus one
   - Command D0 returns garbage bytes from cash drawer
   - Commands C0 and E0 do not appear to function
   - Command F0 will set device into ISP (bootloader) mode

If cash drawer is in ISP (bootloader) mode, it will report a
USB product ID of 0x0c23:

	ID 0d3a:0c23 Posiflex Technologies, Inc. USB  MSR  BL V200

In this case, the Posiflex firmware programming util (available
from manufacturer tech support) can be used to revert the
device to HID mode and restore function. The tool may also be
used to convert the device to "Virtual Com Port" mode which
may be more convenient.
