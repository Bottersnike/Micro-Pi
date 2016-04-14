# Copyright (C) 2014-2015 ARM Limited. All rights reserved.

if(TARGET_NORDIC_NRF51822_16K_GCC_TOOLCHAIN_INCLUDED)
    return()
endif()
set(TARGET_NORDIC_NRF51822_16K_GCC_TOOLCHAIN_INCLUDED 1)

# legacy definitions for building mbed 2.0 modules with a retrofitted build
# system:
set(MBED_LEGACY_TARGET_DEFINITIONS "NORDIC" "NRF51_MICROBIT" "MCU_NRF51822" "MCU_NRF51_16K" "MCU_NORDIC_16K" "MCU_NRF51_16K_S110")
# provide compatibility definitions for compiling with this target: these are
# definitions that legacy code assumes will be defined.
add_definitions("-DNRF51 -DTARGET_NORDIC -DTARGET_M0 -D__MBED__=1 -DMCU_NORDIC_16K -DTARGET_NRF51_MICROBIT -DTARGET_MCU_NORDIC_16K -DTARGET_MCU_NRF51_16K_S110  -DTARGET_NRF_LFCLK_RC -DTARGET_MCU_NORDIC_16K -D__CORTEX_M0 -DARM_MATH_CM0")

# append non-generic flags, and set NRF51822-specific link script
set(_CPU_COMPILATION_OPTIONS "-mcpu=cortex-m0 -mthumb -D__thumb2__")

set(CMAKE_C_FLAGS_INIT             "${CMAKE_C_FLAGS_INIT} ${_CPU_COMPILATION_OPTIONS}")
set(CMAKE_ASM_FLAGS_INIT           "${CMAKE_ASM_FLAGS_INIT} ${_CPU_COMPILATION_OPTIONS}")
set(CMAKE_CXX_FLAGS_INIT           "${CMAKE_CXX_FLAGS_INIT} ${_CPU_COMPILATION_OPTIONS} -std=c++11 -fwrapv")
set(CMAKE_MODULE_LINKER_FLAGS_INIT "${CMAKE_MODULE_LINKER_FLAGS_INIT} -mcpu=cortex-m0 -mthumb")
set(CMAKE_EXE_LINKER_FLAGS_INIT    "${CMAKE_EXE_LINKER_FLAGS_INIT} -mcpu=cortex-m0 -mthumb -T${CMAKE_CURRENT_LIST_DIR}/../ld/NRF51822.ld")

# used by the apply_target_rules function below:
set(NRF51822_SOFTDEVICE_HEX_FILE "${CMAKE_CURRENT_LIST_DIR}/../softdevice/s110_nrf51822_8.0.0_softdevice.hex")
set(NRF51822_BOOTLOADER_HEX_FILE "${CMAKE_CURRENT_LIST_DIR}/../bootloader/BLE_BOOTLOADER_RESERVED.hex")

# define a function for yotta to apply target-specific rules to build products,
# in our case we need to convert the built elf file to .hex, and add the
# pre-built softdevice:
function(yotta_apply_target_rules target_type target_name)
    if(${target_type} STREQUAL "EXECUTABLE")
        add_custom_command(TARGET ${target_name}
            POST_BUILD
            # objcopy to hex
            COMMAND arm-none-eabi-objcopy -O ihex ${target_name} ${target_name}.hex
            # and append the softdevice hex file
            COMMAND srec_cat ${NRF51822_BOOTLOADER_HEX_FILE} -intel ${NRF51822_SOFTDEVICE_HEX_FILE} -intel ${target_name}.hex -intel -o ${target_name}-combined.hex -intel --line-length=44
            COMMENT "hexifying and adding softdevice to ${target_name}"
            VERBATIM
        )
    endif()
endfunction()
