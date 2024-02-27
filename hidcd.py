# SPDX-License-Identifier: MIT
"""Example interface for Posiflex USB HID Cash Drawer

Usage:

	from hidcd import HidCd
	cd = HidCd(7)  # use cash drawer with id=7
	if cd.closed():
            cd.open()

"""

import hidapi
import logging

_log = logging.getLogger('hidcd')
_log.setLevel(logging.INFO)

# Read/Write request len (from descdiption)
_CMDLEN = 120
# USB Vendor ID
_USBVID = 0x0d3a
# USB PRoduct ID (base)
_USBPID = 0x0200
# Read timeout
_TIMEOUTMS = 200


class HidCd:
    """Posiflex USB HID Cash Drawer"""

    def __init__(self, cdnum=None):
        """Find and connect to first matching usb cash drawer"""
        self.cdnum = cdnum
        self._cd = None
        self.__find()

    def connected(self):
        """Return true if drawer connected"""
        return self._cd is not None

    def __find(self):
        """Find first matching HID cash drawer"""
        for dev in hidapi.enumerate(vendor_id=_USBVID):
            if dev.product_id & _USBPID == _USBPID:
                cdnum = dev.product_id & 0x7
                if self.cdnum is None or cdnum == self.cdnum:
                    self._cd = hidapi.Device(dev)
                    self.cdnum = cdnum
                    _log.debug('Found HID cash drawer: %04x:%04x cdnum=%d',
                               _USBVID, dev.product_id, cdnum)
                    break
        if self._cd is None:
            _log.warning('No HID cash drawer found')

    def _write(self, buf):
        if self.connected():
            _log.debug('SEND: %r', buf)
            self._cd.write(buf)

    def _read(self):
        if self.connected():
            res = self._cd.read(_CMDLEN, timeout_ms=_TIMEOUTMS)
            _log.debug('RECV: %r', res)
            return res

    def closed(self):
        """Return true if cash drawer is closed"""
        closed = True
        if self.connected():
            cmd = bytearray(_CMDLEN)
            cmd[0] = self.cdnum
            cmd[1] = self.cdnum + 1
            self._write(cmd)
            res = self._read()
            if res is not None and len(res) > 0:
                state = res[0]
                mask = self.cdnum << 4
                if state & mask == mask:
                    closed = bool(state & 1)
            _log.debug('Drawer closed: %r', closed)
        else:
            raise RuntimeError('No HID drawer connected')
        return closed

    def open(self):
        """Open cash drawer"""
        if self.connected():
            cmd = bytearray(_CMDLEN)
            cmd[0] = self.cdnum
            cmd[1] = self.cdnum
            self._write(cmd)
        else:
            raise RuntimeError('No HID drawer connected')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    _log.setLevel(logging.DEBUG)
    cd = HidCd()
    if cd.connected():
        if cd.closed():
            cd.open()
