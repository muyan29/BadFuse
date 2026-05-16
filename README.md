# Artifact for BadFuse Attack

This is the artifact for the BadFuse Attack, which introduces how to use arbitrary code execution on the ASP to permanently alter the root of trust on the Milan processor. This is achieved by burning the fuse at the `Custom_PK` location. The purpose of this experiment is to extract the VCEK root seed; if you only need arbitrary code execution on the ASP, [MilanLaunchy](https://github.com/muyan29/MilanLaunchy) is sufficient.

## Before Reproducing

Please read the BadFuse Attack Part I in [this paper](https://arxiv.org/abs/2605.12990) to understand how this attack works, its impact, and our responsible disclosure.

**Please carefully read the following description of the risks.**

**Please note that reproducing this experiment will have an irreversible impact on your chip! Please note that once you start reproducing this experiment, your Milan processor will no longer be usable in a normal manner!**

**In an ideal scenario:** You obtain a Milan CPU with your customized root of trust. Because you possess the private key corresponding to the public key, you can sign any off-chip bootloader, including an off-chip bootloader with SVN=255.

> Please note that once the burning is complete, the original AMD public key will become invalid, and the CPU will only accept your Custom_PK.

**In an undesired scenario:** If you burn the Custom_PK incorrectly (for example, only successfully burning a portion of it), this will permanently and irreversibly brick your chip.

As incorrect operations may lead to the chip getting bricked, causing financial loss, I strongly recommend using a cheaper model of EPYC Milan to reproduce this experiment to avoid property damage. **Please note that the author assumes no responsibility or liability for any damage, data loss, or system instability caused by reproducing this experiment.**

## Stage0

Reproducing this experiment requires arbitrary code execution capabilities on ASP. Please ensure that you have successfully reproduced [MilanLaunchy](https://github.com/muyan29/MilanLaunchy).

> Please use a clean EPYC Milan to complete the experiment. This chip should not have had any fuses burned previously (it is not recommended to use a vendor-locked Milan CPU for this experiment).

## Stage1-preparepk

You need to prepare your own public and private keys that meet the formatting requirements and calculate the SHA384 hash of the public key. This SHA384 hash will be written in the next stage. Please keep your private key safe; you will need this private key to sign the off-chip bootloader.

## Stage2-burnfuse

You need to burn this SHA384 hash to the correct location. Only the core code is provided here; for researchers in this field, it's not hard to execute this code. The underlying principle is calling a fuse-burning function originally encapsulated within the off-chip bootloader, the offset address of which is calculated based on the off-chip bootloader in the S8036V206 firmware.

> I do not know why calling the function only once will cause the burning to fail; in my code, the function was called twice for every 32 bits to perform the burning.

## Stage3-gene-new-image

At this point, your public key of your Milan chip has changed, and if you reboot the system, you will find that it fails to boot. Now you need to use a BMC or SPI-Flash programmer to flash the new firmware. You need to create a new firmware image, which includes your own public key and the off-chip bootloader signed with your own private key. In order to successfully boot the x86 system, you also need to hook the RSA signature verification in the off-chip bootloader to successfully load various components signed by AMD, such as the ABL, SMU, etc.

## Extracting the VCEK Seed

Now you have the capability of arbitrary code execution on the off-chip bootloader with SVN=255. For researchers in this field, it's not hard to extract the VCEK seed. After extraction, you can use [this script](https://github.com/PSPReverse/amd-sp-glitch/blob/main/payloads/bl_seed_to_vcek.py) to generate the private key for any version of VCEK.

If you have any issues while reproducing this attack, feel free to contact me.

## Contact Me

Muyan Shen

Email: cwindy2024@outlook.com

