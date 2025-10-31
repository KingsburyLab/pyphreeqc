from pathlib import Path
import numpy as np
from pyphreeqc.interface import Phreeqc


def test_load_database_internal():
    # `phreeqc.dat` is included with the package, so we don't need to specify
    # `database_directory`.
    phreeqc = Phreeqc(database="phreeqc.dat")


def test_load_database_external():
    # We can always load an external database by specifying
    # `database_directory`.
    phreeqc = Phreeqc(database="phreeqc.dat", database_directory=Path(__file__).parent)


def test_run():
    # TODO: Break this down into individual tests
    phreeqc = Phreeqc("phreeqc.dat")

    phreeqc.run_string("""
        TITLE Example 11.--Transport and ion exchange.
        SOLUTION 0  CaCl2
            units            mmol/kgw
            temp             25.0
            pH               7.0     charge
            pe               12.5    O2(g)   -0.68
            Ca               0.6
            Cl               1.2
        SOLUTION 1  Initial solution for column
            units            mmol/kgw
            temp             25.0
            pH               7.0     charge
            pe               12.5    O2(g)   -0.68
            Na               1.0
            K                0.2
            N(5)             1.2
            END
        EXCHANGE 1
            equilibrate 1
            X                0.0011
        END    
    """)

    assert phreeqc.get_component_count() == 5
    # components are in alphabetic order
    assert phreeqc.get_component(0) == "Ca"
    assert phreeqc.get_component(1) == "Cl"
    assert phreeqc.get_component(2) == "K"
    assert phreeqc.get_component(3) == "N"
    assert phreeqc.get_component(4) == "Na"

    phreeqc.run_string("""
        SELECTED_OUTPUT
            -reset false
        USER_PUNCH
            -headings    cb    H    O    Ca	Cl	K	N	Na	
            10 w = TOT("water")
            20 PUNCH CHARGE_BALANCE, TOTMOLE("H"), TOTMOLE("O")
            30 PUNCH w*TOT("Ca")
            40 PUNCH w*TOT("Cl")
            50 PUNCH w*TOT("K")
            60 PUNCH w*TOT("N")
            70 PUNCH w*TOT("Na")
    """)

    phreeqc.run_string("""
        RUN_CELLS; -cells 0-1
    """)

    assert phreeqc.get_selected_output_row_count() == 3
    assert phreeqc.get_selected_output_column_count() == 8

    # We can get values at a specific index, or a slice
    assert phreeqc[0, 0] == "cb"
    assert phreeqc[0, 1:4] == ["H", "O", "Ca"]
    assert phreeqc[0, 5:] == ["K", "N", "Na"]

    assert np.allclose(
        phreeqc[1, :],
        np.array([2.979292808179192e-18, 111.01243360409575, 55.50675186622646,
                  0.0006000000000000017, 0.0012000000000000005, 0.0, 0.0, 0.0])
    )

    assert np.allclose(
        phreeqc[2],  # single indices are also fine
        np.array(
            [-3.395954270633993e-16, 111.01243360154359, 55.510351938877264,
             0.0, 0.0, 0.00020000000000012212, 0.0012000000000010212,
             0.0010000000000005584])
    )
