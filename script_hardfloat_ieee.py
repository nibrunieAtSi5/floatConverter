import argparse
import random


class IEEEFN:
    def __init__(self, sigSize, expSize):
        self.sigSize = sigSize
        self.expSize = expSize

    @property
    def expInfOrNaN(self):
        return (2**self.expSize-1)
    @property
    def bias(self):
        return -(2**(self.expSize - 1) - 1)

    def toHardFloatRecFN(self):
        """ build the equivalent hardfloat recoded format """
        return HardFloatRecFN(self.sigSize, self.expSize + 1)

    def makeInf(self, sign):
        """ build infinite value with sign """
        return ((sign << self.expSize) | (2**self.expSize - 1)) << (self.sigSize - 1)

    def makeNaN(self, sign=0, qbit=1, payload=None):
        """ build a NaN whose sign is sign, and whose quiet bit is set to qbit """
        if payload:
            return self.makeInf(sign) | payload
        else:
            return self.makeInf(sign) | (2**(self.sigSize-2) - 1) | (qbit << (self.sigSize - 2))

    def buildValue(self, sign, exp, sig):
        """ built an arbitrary value """
        assert 0 <= sign <= 1
        assert 0 <= exp <= (2**self.expSize - 1)
        assert 0 <= sig <= (2**(self.sigSize - 1) - 1)
        return (((sign << self.expSize) | exp) << self.sigSize - 1) | sig

    def isExpInforNaN(self, expValue):
        """ check if encoded expValue is an infinity's exponent """
        return expValue == self.expInfOrNaN
    def isExpZeroOrSubnormal(self, expValue):
        """ check if encoded expValue is a zero's exponent """
        return expValue == 0

class HardFloatRecFN:
    def __init__(self, sigSize, expSize):
        self.sigSize = sigSize
        self.expSize = expSize

    def toIEEEFN(self):
        """ build the equivalent IEEE-754 floating-point encoding """
        return IEEEFN(self.sigSize, self.expSize-1)

    @property
    def minNormalExp(self):
        """ return the format minimal exponent for a normal number """
        return 2**(self.expSize - 2) + 2
    @property
    def minSubNormalExp(self):
        """ return the format minimal exponent for a subnormal number """
        return 2**(self.expSize - 2) + 2 - self.sigSize

    def expNormalToIEEE(self, expValue):
        """ convert the exponent biased value to its IEEE biased encoding
            assuming it is the exponent of a normal number """
        return expValue - 2**(self.expSize - 2) - 1


    def isExpInf(self, expValue):
        """ check if encoded expValue is an infinity's exponent """
        return (expValue >> (self.expSize - 3)) == 0x6
    def isExpNaN(self, expValue):
        """ check if encoded expValue is a NaN's exponent """
        return (expValue >> (self.expSize - 3)) == 0x7
    def isExpZero(self, expValue):
        """ check if encoded expValue is a zero's exponent """
        return (expValue >> (self.expSize - 3)) == 0x0

    def makeInf(self, sign, payload=0):
        """ build infinite value with sign """
        return (((sign << self.expSize) | (0x6 << (self.expSize - 3))) << (self.sigSize - 1)) | payload

    def makeNaN(self, sign=0, qbit=1, payload=0):
        """ build a NaN whose sign is sign, and whose quiet bit is set to qbit """
        return (((sign << self.expSize) | \
               (0x7 << (self.expSize - 3))) << (self.sigSize - 1)) | \
               payload | (qbit << (self.sigSize - 2))

    def buildValue(self, sign, exp, sig):
        """ built an arbitrary value """
        assert 0 <= sign <= 1
        assert 0 <= exp <= (2**self.expSize - 1)
        assert 0 <= sig <= (2**(self.sigSize - 1) - 1)
        return (((sign << self.expSize) | exp) << self.sigSize - 1) | sig


# Map of IEEE-754 standard floating-point formats
IEEE_FORMAT_MAP = {
        16: IEEEFN(11, 5),  # half precision
        32: IEEEFN(24, 8),  # single precision
        64: IEEEFN(53, 11), # double precision
}

# Map of hardfloat's recoded floating-point formats
HARDFLOAT_FORMAT_MAP = {s: IEEE_FORMAT_MAP[s].toHardFloatRecFN() for s in IEEE_FORMAT_MAP}

def bitMask(size):
    """ generate a ful set bit mask of width <size> """
    return 2**size - 1

def RecFNtoIEEE_s2i(v, base=16, size=64):
    """ convert a string-encoded value <v> from recoded to IEEE format """
    v = v.replace("_", "")
    v = int(v, base=base)
    return RecFNtoIEEE(v, size=size)

def RecFNtoIEEE(v, base=16, size=64):
    """ convert a value <v> from recoded format to IEEE format """
    recfn = HARDFLOAT_FORMAT_MAP[size]
    SIGMASK = bitMask(recfn.sigSize - 1)
    sig = v & SIGMASK
    EXPMASK = bitMask(recfn.expSize)
    exp = (v >> (recfn.sigSize - 1)) & EXPMASK
    sign = (v >> (recfn.sigSize - 1 + recfn.expSize)) & 0x1
    ieeefn = recfn.toIEEEFN()
    ieee_sign = sign << (ieeefn.sigSize - 1 + ieeefn.expSize) 
    if recfn.isExpZero(exp):
        return ieee_sign 
    elif recfn.isExpInf(exp):
        return ieeefn.makeInf(sign) 
    elif recfn.isExpNaN(exp):
        # todo/fixme: payload forwarding
        assert sig != 0, "NaN payload cannot be equal to zero in recoded format"
        return ieeefn.makeNaN(sign, payload=sig)
    elif exp < recfn.minNormalExp:
        assert exp >= recfn.minSubNormalExp, "invalid exponent"
        lzc = recfn.minNormalExp - exp
        maskOffOne = (1 << (recfn.sigSize - 1))
        assert ((sig >> lzc) << lzc) == sig, "subnormal significand must not have bit set with weight <= emin - s"
        return ieeefn.buildValue(sign, 0, (sig | maskOffOne) >> lzc)
    else:
        return ieeefn.buildValue(sign, recfn.expNormalToIEEE(exp),sig) 

def lzc(value, size):
    """ Leading Zero Count """
    count = 0
    index = size - 1
    while (value >> index) == 0 and index >= 0:
        count += 1
        index -= 1
    return count

def IEEEtoRecFN(v, base=16, size=64, randomizePayload=True):
    ieeeFmt = IEEE_FORMAT_MAP[size]
    recfn = ieeeFmt.toHardFloatRecFN()

    SIGMASK = bitMask(ieeeFmt.sigSize - 1)
    sig = v & SIGMASK
    EXPMASK = bitMask(ieeeFmt.expSize)
    exp = (v >> (ieeeFmt.sigSize - 1)) & EXPMASK
    sign = (v >> (ieeeFmt.sigSize - 1 + ieeeFmt.expSize)) & 0x1
    if ieeeFmt.isExpInforNaN(exp):
        if sig == 0:
            # infinity
            infPayload = random.randrange(2**(ieeeFmt.sigSize - 1)) if randomizePayload else 0
            return recfn.makeInf(sign, payload=infPayload)
        else:
            # NaN
            return recfn.makeNaN(sign, qbit=(sig >> (ieeeFmt.sigSize - 2)), payload=sig)
    elif ieeeFmt.isExpZeroOrSubnormal(exp):
        if sig == 0:
            # zero
            return recfn.buildValue(sign, 0, 0)
        else:
            # subnormal
            normShift = lzc(sig, ieeeFmt.sigSize - 1)
            # normalizing significand and removing implicit one
            sig = (sig << (normShift + 1)) & SIGMASK
            biasedExp = recfn.minNormalExp - 1 - normShift
            return recfn.buildValue(sign, biasedExp, sig)
    else:
        # normal
        biasedExp = (exp - 1) + recfn.minNormalExp
        return recfn.buildValue(sign, biasedExp, sig)

def IEEEToRecFN_s2i(v, base=16, size=64, randomizePayload=True):
    """ convert a string-encoded value <v> from recoded to IEEE format """
    v = v.replace("_", "")
    v = int(v, base=base)
    return IEEEtoRecFN(v, size=size, randomizePayload=randomizePayload)

assert(lzc(0xff, 8) == 0)
assert(lzc(0xf, 13) == 9)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='hardfloat/IEEE converter')
    parser.add_argument('command', type=str, choices=["recfntoieee", "ieeetorecfn"],
                        help='command to be executed')
    parser.add_argument('values', metavar='V', type=str, nargs='+',
                        help='value')
    parser.add_argument('--input-size', type=int, action='store', default=64,
                        help='input value size')
    parser.add_argument('--payload-to-zero', const=True, default=False, action='store_const', 
                        help='force don\'t care RecFN payload to zero')

    args = parser.parse_args()
    for value in args.values[0].split(','):
        if args.command == "recfntoieee":
            print(hex(RecFNtoIEEE_s2i(value, base=16, size=args.input_size))) 
        elif args.command == "ieeetorecfn":
            print(hex(IEEEToRecFN_s2i(value, base=16, size=args.input_size, randomizePayload=not args.payload_to_zero))) 
        else:
            raise NotImplementedError



