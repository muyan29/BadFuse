
PROVIDE(bl_mapsmn_on_die = 0x9e8c+1);
PROVIDE(burn_fuse = 0x8604+1);

SECTIONS
{
  . = 0x30000;
  .text ALIGN(0x10): { *(.text) }
  .data ALIGN(0x20) : { *(.data) }
}
