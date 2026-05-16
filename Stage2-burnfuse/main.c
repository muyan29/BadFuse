#include <stdalign.h>
#include <stdint.h>
#include "fw_func.h"


__attribute__((target("thumb"))) int main () {

        ret = 0;
        // burn fuse sha384(my_publickey), do it twice...
        // sha384sum pkmilan_myself
        //a395b31660b7f7d2a98b43c652e758c89b9a53caebf5022a27de32af9fd69b44753618c15e8bd06e6297389a364e33f7  pkmilan_myself
    // Word 0: Bytes [0-3]
    ret += burn_fuse(0x1D, 0x16b395a3, 0); // a3 95 b3 16
    ret += burn_fuse(0x1D, 0x16b395a3, 0);
    // Word 1: Bytes [4-7]
    ret += burn_fuse(0x1E, 0xd2f7b760, 0); // 60 b7 f7 d2
    ret += burn_fuse(0x1E, 0xd2f7b760, 0);
    // Word 2: Bytes [8-11]
    ret += burn_fuse(0x1F, 0xc6438ba9, 0); // a9 8b 43 c6
    ret += burn_fuse(0x1F, 0xc6438ba9, 0);
    // Word 3: Bytes [12-15]
    ret += burn_fuse(0x20, 0xc858e752, 0); // 52 e7 58 c8
    ret += burn_fuse(0x20, 0xc858e752, 0);
    // Word 4: Bytes [16-19]
    ret += burn_fuse(0x21, 0xca539a9b, 0); // 9b 9a 53 ca
    ret += burn_fuse(0x21, 0xca539a9b, 0);
    // Word 5: Bytes [20-23]
    ret += burn_fuse(0x22, 0x2a02f5eb, 0); // eb f5 02 2a
    ret += burn_fuse(0x22, 0x2a02f5eb, 0);
    // Word 6: Bytes [24-27]
    ret += burn_fuse(0x23, 0xaf32de27, 0); // 27 de 32 af
    ret += burn_fuse(0x23, 0xaf32de27, 0);
    // Word 7: Bytes [28-31]
    ret += burn_fuse(0x24, 0x449bd69f, 0); // 9f d6 9b 44
    ret += burn_fuse(0x24, 0x449bd69f, 0);
    // Word 8: Bytes [32-35]
    ret += burn_fuse(0x25, 0xc1183675, 0); // 75 36 18 c1
    ret += burn_fuse(0x25, 0xc1183675, 0);
    // Word 9: Bytes [36-39]
    ret += burn_fuse(0x26, 0x6ed08b5e, 0); // 5e 8b d0 6e
    ret += burn_fuse(0x26, 0x6ed08b5e, 0);
    // Word 10: Bytes [40-43]
    ret += burn_fuse(0x27, 0x9a389762, 0); // 62 97 38 9a
    ret += burn_fuse(0x27, 0x9a389762, 0);
    // Word 11: Bytes [44-47]
    ret += burn_fuse(0x28, 0xf7334e36, 0); // 36 4e 33 f7
    ret += burn_fuse(0x28, 0xf7334e36, 0);
    
    if (ret != 0)
   	    return ret; 
    return 0;
}




