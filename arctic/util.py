def set_min_max(value, min, max):
    """ Fix a value between a minimum and maximum. """
    if value < min:
        return min
    elif max < value:
        return max
    else:
        return value


def update_fits_header_info(
    ext_header,
    parallel_clocker=None,
    serial_clocker=None,
    parallel_traps=None,
    serial_traps=None,
    parallel_ccd_volume=None,
    serial_ccd_volume=None,
):
    """Update a fits header to include the parallel CTI settings.

    Params
    -----------
    ext_header : astropy.io.hdulist
        The opened header of the astropy fits header.
    """

    if parallel_clocker is not None:
        ext_header.set(
            "cte_pite",
            parallel_clocker.iterations,
            "Iterations Used In Correction (Parallel)",
        )
        # ext_header.set(
        #     "cte_pwld", parallel_clocker.well_depth, "CCD Well Depth (Parallel)"
        # )

    if serial_clocker is not None:
        ext_header.set(
            "cte_site",
            serial_clocker.iterations,
            "Iterations Used In Correction (Serial)",
        )
        # ext_header.set(
        #     "cte_swld", serial_clocker.well_depth, "CCD Well Depth (Serial)"
        # )

        def add_trap(name, traps):
            for i, trap in traps:
                ext_header.set(
                    "cte_pt{}d".format(i),
                    trap.trap_density,
                    "Trap trap {} density ({})".format(i, name),
                )
                ext_header.set(
                    "cte_pt{}t".format(i),
                    trap.trap_lifetime,
                    "Trap trap {} lifetime ({})".format(i, name),
                )

        if parallel_traps is not None:
            add_trap(name="Parallel", traps=parallel_traps)

        if serial_traps is not None:
            add_trap(name="Serial", traps=serial_traps)

        if serial_ccd_volume is not None:
            ext_header.set(
                "cte_swln",
                serial_ccd_volume.well_notch_depth,
                "CCD Well notch depth (Serial)",
            )
            ext_header.set(
                "cte_swlp",
                serial_ccd_volume.well_fill_beta,
                "CCD Well filling power (Serial)",
            )

        if parallel_ccd_volume is not None:
            ext_header.set(
                "cte_pwln",
                parallel_ccd_volume.well_notch_depth,
                "CCD Well notch depth (Parallel)",
            )
            ext_header.set(
                "cte_pwlp",
                parallel_ccd_volume.well_fill_beta,
                "CCD Well filling power (Parallel)",
            )

        return ext_header

    return ext_header
