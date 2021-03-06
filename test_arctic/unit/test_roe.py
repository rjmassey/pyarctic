import numpy as np
import pytest

import arctic as ac


class TestExpress:

    #    def test__trailing_of_trails(self):
    #        assert False, "TBD"

    def test__express_matrix_from_pixels(self):

        roe = ac.ROE(empty_traps_at_start=False)
        express_multiplier, _ = roe.express_matrix_from_pixels_and_express(
            pixels=12, express=1, dtype=int
        )

        assert express_multiplier == pytest.approx(np.array([np.arange(1, 13)]))

        express_multiplier, _ = roe.express_matrix_from_pixels_and_express(
            pixels=12, express=4, dtype=int
        )

        assert express_multiplier == pytest.approx(
            np.array(
                [
                    [1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
                    [0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3],
                    [0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 3],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3],
                ]
            )
        )

        express_multiplier, _ = roe.express_matrix_from_pixels_and_express(
            pixels=12, express=12
        )

        assert express_multiplier == pytest.approx(np.triu(np.ones((12, 12))))

        roe = ac.ROE(empty_traps_at_start=True)
        express_multiplier, _ = roe.express_matrix_from_pixels_and_express(
            pixels=12, express=12
        )

    def test__express_matrix_always_sums_to_n_transfers(self):
        for pixels in [5, 7, 17]:
            for express in [0, 1, 2, 7]:
                for offset in [0, 1, 13]:
                    for dtype in [int, float]:
                        for first_pixel_different in [True, False]:
                            roe = ac.ROE(empty_traps_at_start=first_pixel_different)
                            (
                                express_multiplier,
                                _,
                            ) = roe.express_matrix_from_pixels_and_express(
                                pixels=pixels,
                                express=express,
                                offset=offset,
                                dtype=dtype,
                            )
                            assert np.sum(express_multiplier, axis=0) == pytest.approx(
                                np.arange(1, pixels + 1) + offset
                            )


class TestClockingSequences:
    def test__release_fractions_sum_to_unity(self):

        for n_phases in [1, 2, 3, 4]:
            roe = ac.ROETrapPumping([1] * (n_phases * 2))
            for step in roe.clock_sequence:
                for phase in step:
                    assert sum(phase["release_fraction_to_pixel"]) == 1

    def test__readout_sequence_single_phase_single_phase_high(self):

        for force_downstream_release in [True, False]:
            roe = ac.ROE([1], force_downstream_release=force_downstream_release)
            assert roe.pixels_accessed_during_clocking == [0]
            # assert min(roe.pixels_accessed_during_clocking) == 0
            # assert max(roe.pixels_accessed_during_clocking) == 0
            assert roe.n_phases == 1
            assert roe.n_steps == 1
            assert roe.clock_sequence[0][0]["high"], "Highness"
            assert roe.clock_sequence[0][0]["capture_from_which_pixel"] == 0
            assert roe.clock_sequence[0][0]["release_to_which_pixel"] == 0

    def test__readout_sequence_two_phase_single_phase_high(self):

        n_phases = 2

        roe = ac.ROE([1] * n_phases, force_downstream_release=False)
        assert roe.pixels_accessed_during_clocking == [-1, 0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == -1
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert (
            roe.clock_sequence[0][1]["release_to_which_pixel"] == np.array([-1, 0])
        ).all
        assert (
            roe.clock_sequence[1][0]["release_to_which_pixel"] == np.array([0, 1])
        ).all

        roe = ac.ROE([1] * n_phases, force_downstream_release=True)
        assert roe.pixels_accessed_during_clocking == [0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == 0
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert (
            roe.clock_sequence[0][1]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert (
            roe.clock_sequence[1][0]["release_to_which_pixel"] == np.array([0, 1])
        ).all

    def test__readout_sequence_three_phase_single_phase_high(self):

        n_phases = 3

        roe = ac.ROE([1] * n_phases, force_downstream_release=False)
        assert roe.pixels_accessed_during_clocking == [-1, 0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == -1
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert roe.clock_sequence[0][1]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[0][2]["release_to_which_pixel"] == -1
        assert roe.clock_sequence[1][0]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][2]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[2][0]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[2][1]["release_to_which_pixel"] == 0

        # Never move electrons ahead of the trap
        roe = ac.ROE([1] * n_phases, force_downstream_release=True)
        assert roe.pixels_accessed_during_clocking == [0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == 0
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        # Check all high phases
        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert roe.clock_sequence[0][1]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[0][2]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][0]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][2]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[2][0]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[2][1]["release_to_which_pixel"] == 0

    def test__trappumping_sequence_three_phase_single_phase_high(self):

        n_phases = 3

        roe = ac.ROETrapPumping([1] * (2 * n_phases))
        assert roe.pixels_accessed_during_clocking == [-1, 0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == -1
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == 2 * n_phases

        for step in range(roe.n_steps):
            phase = ([0, 1, 2, 0, 2, 1])[step]
            assert roe.clock_sequence[step][phase]["high"], "Highness"
        assert roe.clock_sequence[3][0]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[3][1]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[3][2]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[4] == roe.clock_sequence[2]
        assert roe.clock_sequence[5] == roe.clock_sequence[1]

    def test__readout_sequence_four_phase_single_phase_high(self):

        n_phases = 4

        roe = ac.ROE([1] * n_phases, force_downstream_release=False)
        assert roe.pixels_accessed_during_clocking == [-1, 0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == -1
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert roe.clock_sequence[0][1]["release_to_which_pixel"] == 0
        assert (
            roe.clock_sequence[0][2]["release_to_which_pixel"] == np.array([-1, 0])
        ).all
        assert roe.clock_sequence[0][3]["release_to_which_pixel"] == -1
        assert roe.clock_sequence[1][0]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][2]["release_to_which_pixel"] == 0
        assert (
            roe.clock_sequence[1][3]["release_to_which_pixel"] == np.array([-1, 0])
        ).all
        assert (
            roe.clock_sequence[2][0]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert roe.clock_sequence[2][1]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[2][3]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[3][0]["release_to_which_pixel"] == 1
        assert (
            roe.clock_sequence[3][1]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert roe.clock_sequence[3][2]["release_to_which_pixel"] == 0

        roe = ac.ROE([1] * n_phases, force_downstream_release=True)
        assert roe.pixels_accessed_during_clocking == [0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == 0
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == n_phases

        for step in range(n_phases):
            phase = step
            assert roe.clock_sequence[step][phase]["high"], "Highness"
            assert (
                roe.clock_sequence[step][phase]["capture_from_which_pixel"] == 0
            ), "Step {}, phase {}, capture".format(step, phase)
            assert (
                roe.clock_sequence[step][phase]["release_to_which_pixel"] == 0
            ), "Step {}, phase {}, release".format(step, phase)

        # Check other phases
        assert roe.clock_sequence[0][1]["release_to_which_pixel"] == 1
        assert (
            roe.clock_sequence[0][2]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert roe.clock_sequence[0][3]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][0]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[1][2]["release_to_which_pixel"] == 1
        assert (
            roe.clock_sequence[1][3]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert (
            roe.clock_sequence[2][0]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert roe.clock_sequence[2][1]["release_to_which_pixel"] == 0
        assert roe.clock_sequence[2][3]["release_to_which_pixel"] == 1
        assert roe.clock_sequence[3][0]["release_to_which_pixel"] == 1
        assert (
            roe.clock_sequence[3][1]["release_to_which_pixel"] == np.array([0, 1])
        ).all
        assert roe.clock_sequence[3][2]["release_to_which_pixel"] == 0

    def test__trappumping_sequence_four_phase_single_phase_high(self):

        n_phases = 4
        roe = ac.ROETrapPumping([1] * (2 * n_phases))
        assert roe.pixels_accessed_during_clocking == [-1, 0, 1]
        # assert min(roe.pixels_accessed_during_clocking) == -1
        # assert max(roe.pixels_accessed_during_clocking) == +1
        assert roe.n_phases == n_phases
        assert roe.n_steps == 2 * n_phases

        for step in range(roe.n_steps):
            phase = ([0, 1, 2, 3, 0, 3, 2, 1])[step]
            assert roe.clock_sequence[step][phase]["high"], "Highness"


class TestTrapPumpingResults:
    def test__serial_trap_pumping_in_different_phases_makes_dipole(self):

        # 3-phase pocket pumping with traps under phase 1 - no change expected
        injection_level = 1000
        image_orig = np.zeros((5, 1)) + injection_level
        trap_pixel = 2
        trap = ac.TrapInstantCapture(density=100, release_timescale=3)
        roe = ac.ROETrapPumping(dwell_times=[1] * 6, n_pumps=2)
        ccd = ac.CCD(
            well_fill_power=0.5, full_well_depth=2e5, fraction_of_traps=[1, 0, 0]
        )
        image_cti = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
        )
        assert (
            image_cti[trap_pixel] < image_orig[trap_pixel]
        ), "pumping a trap in phase 1 does not remove charge"
        assert abs(image_cti[trap_pixel] - image_orig[trap_pixel]) > abs(
            image_cti[trap_pixel + 1] - image_orig[trap_pixel + 1]
        ), "pumping a trap in phase 1 affects -neighbouring pixels"
        assert abs(image_cti[trap_pixel] - image_orig[trap_pixel]) > abs(
            image_cti[trap_pixel + 1] - image_orig[trap_pixel + 1]
        ), "pumping a trap in phase 1 affects -neighbouring pixels"

        # Traps under phase 2 - check for dipole
        ccd = ac.CCD(
            well_fill_power=0.5, full_well_depth=2e5, fraction_of_traps=[0, 1, 0]
        )
        image_cti = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
        )
        assert (
            image_cti[trap_pixel] < image_orig[trap_pixel]
        ), "pumping a trap in phase 2 does not remove charge"
        assert (
            image_cti[trap_pixel + 1] > image_orig[trap_pixel + 1]
        ), "pumping a trap in phase 2 doesn't make a dipole"

        # Traps under phase 3 - check for dipole
        ccd = ac.CCD(
            well_fill_power=0.5, full_well_depth=2e5, fraction_of_traps=[0, 0, 1]
        )
        image_cti = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
        )
        assert (
            image_cti[trap_pixel] < image_orig[trap_pixel]
        ), "pumping a trap in phase 3 does not remove charge"
        assert (
            image_cti[trap_pixel - 1] > image_orig[trap_pixel - 1]
        ), "pumping a trap in phase 3 doesn't make a dipole"

    def test__express_is_good_approximation_for_trap_pumping(self):

        # 3-phase pocket pumping with traps under phase 1 - no change expected
        injection_level = 1000
        image_orig = np.zeros((5, 1)) + injection_level
        trap_pixel = 2
        trap_density = 1
        n_pumps = 20
        ccd = ac.CCD(
            well_notch_depth=100, full_well_depth=101, fraction_of_traps=[0, 1, 0]
        )
        trap = ac.TrapInstantCapture(density=trap_density, release_timescale=0.5)
        roe = ac.ROETrapPumping(dwell_times=[0.33] * 6, n_pumps=n_pumps)

        image_cti_express0 = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
            parallel_express=0,
        )

        image_cti_express1 = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
            parallel_express=1,
        )

        image_cti_express3 = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
            parallel_express=3,
        )

        fractional_diff_01 = (
            image_cti_express1[[trap_pixel, trap_pixel + 1]]
            - image_cti_express0[[trap_pixel, trap_pixel + 1]]
        ) / image_orig[[trap_pixel, trap_pixel + 1]]
        fractional_diff_03 = (
            image_cti_express3[[trap_pixel, trap_pixel + 1]]
            - image_cti_express0[[trap_pixel, trap_pixel + 1]]
        ) / image_orig[[trap_pixel, trap_pixel + 1]]

        assert (
            abs(fractional_diff_01) < 1e-7
        ).all, "changing express from 0 (slow) to 1 (fast)"
        assert (
            abs(fractional_diff_03) < 1e-7
        ).all, "changing express from 0 (slow) to 3 (fastish)"

        # Add more traps
        density_change = 2
        traphighrho = ac.TrapInstantCapture(
            density=(trap_density * density_change), release_timescale=0.5
        )
        image_cti_express1_highrho = ac.add_cti(
            image=image_orig,
            parallel_traps=[traphighrho],
            parallel_ccd=ccd,
            parallel_roe=roe,
            parallel_window=trap_pixel,
            parallel_express=1,
        )
        fractional_diff = (
            (
                image_cti_express1_highrho[[trap_pixel, trap_pixel + 1]]
                - image_orig[[trap_pixel, trap_pixel + 1]]
            )
            - density_change
            * (
                image_cti_express1[[trap_pixel, trap_pixel + 1]]
                - image_orig[[trap_pixel, trap_pixel + 1]]
            )
        ) / image_orig[[trap_pixel, trap_pixel + 1]]
        assert (abs(fractional_diff) < 1e-7).all

        # Do more pumps
        n_pumps_change = 10
        roehighpumps = ac.ROETrapPumping(
            dwell_times=[0.33] * 6, n_pumps=(n_pumps * n_pumps_change)
        )
        image_cti_express1_highpump = ac.add_cti(
            image=image_orig,
            parallel_traps=[trap],
            parallel_ccd=ccd,
            parallel_roe=roehighpumps,
            parallel_window=trap_pixel,
            parallel_express=1,
        )
        fractional_diff = (
            (
                image_cti_express1_highpump[[trap_pixel, trap_pixel + 1]]
                - image_orig[[trap_pixel, trap_pixel + 1]]
            )
            - n_pumps_change
            * (
                image_cti_express1[[trap_pixel, trap_pixel + 1]]
                - image_orig[[trap_pixel, trap_pixel + 1]]
            )
        ) / image_orig[[trap_pixel, trap_pixel + 1]]
        assert (abs(fractional_diff) < 1e-7).all


#    def test__express_is_good_approximation_for_charge_injection(self):
#
#        roe = ac.ROEChargeInjection(n_active_pixels=2)
#        express_matrix, _ = roe.express_matrix_from_pixels_and_express(10,0)
#        express_matrix.shape
#
#        ccd = ac.CCD(well_fill_power=0.5, full_well_depth=2e5)
#        roe = ac.ROEChargeInjection(n_active_pixels=2000)
#        trap = ac.Trap(density=1, release_timescale=0.5)
#
#        background = 0
#        image_orig = np.zeros((9, 1)) + background
#        image_orig[0] = 1e5
#
#        image_cti = ac.add_cti(
#            image=image_orig,
#            parallel_traps=[trap],
#            parallel_ccd=ccd,
#            parallel_roe=roe,
#        )
#
#
#
#
#
#        ccd = ac.CCD(well_fill_power=0.5, full_well_depth=2e5)
#        roe = ac.ROE()
#        trap = ac.Trap(density=1, release_timescale=0.5)
#
#        background = 0
#        image_orig = np.zeros((9, 1)) + background
#        image_orig[0] = 1e5
#
#        image_cti = ac.add_cti(
#            image=image_orig,
#            parallel_traps=[trap],
#            parallel_ccd=ccd,
#            parallel_roe=roe,
#            parallel_offset=2000,
#        )
#        plt.plot(image_cti)
#        plt.yscale("log")
#
#
#
#
#
#
#        ccd = ac.CCD(well_fill_power=1, full_well_depth=2e5, fraction_of_traps=[0.33,0.33,0.33])
#        roe = ac.ROEChargeInjection(dwell_times=[0.33,0.33,0.33], force_downstream_release = False,n_active_pixels=2000)
#        trap = ac.Trap(density=10, release_timescale=0.5)
#
#        background = 0
#        image_orig = np.zeros((9, 1)) + background
#        image_orig[0] = 1e5
#
#        image_cti = ac.add_cti(
#            image=image_orig,
#            parallel_traps=[trap],
#            parallel_ccd=ccd,
#            parallel_roe=roe,
#        )
#        plt.plot(image_cti)
#        plt.yscale("log")

# class TestReadoutResults:
#
#    def test__express_is_good_approximation_for_readout(self):
