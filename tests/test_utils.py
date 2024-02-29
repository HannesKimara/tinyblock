from unittest import TestCase

from tinyblock.utils import base58_encode


class Base58Test(TestCase):
    def test_encode(self):
        vals = {
            '7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d': '9MA8fRQrT4u8Zj8ZRd6MAiiyaxb2Y1CMpvVkHQu5hVM6',
            'eff69ef2b1bd93a66ed5219add4fb51e11a840f404876325a1e8ffe0529a2c': '4fE3H2E6XMp4SsxtwinF7w9a34ooUrwWe4WsW1458Pd',
            'c7207fee197d27c618aea621406f6bf5ef6fca38681d82b2f06fddbdce6feab6': 'EQJsjkd6JaGwxrjEhfeqPenqHwrBmPQZjJGNSCHBkcF7'
        }

        for k,v in vals.items():
            harray = bytes().fromhex(k)
            enh = base58_encode(harray)

            self.assertEqual(enh, v)
