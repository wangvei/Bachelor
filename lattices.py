# Lattice plotting
import itertools

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

eq = np.isclose

# Defaults for creator
d = (np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1]),
     np.array([0, 0, 0]), "xkcd:cement", 2, "proper", "latticevectors",
     [0, 0, 0], [2, 2, 2])

latticelines = {'base centred cubic': 'soft',
                'base centred monoclinic 1': 'latticevectors',
                'base centred monoclinic 2': 'latticevectors',
                'base centred monoclinic 3': 'latticevectors',
                'bcc': 'soft',
                'conventional bcc': 'soft',
                'conventional fcc': 'soft',
                'fcc': 'soft',
                'hexagonal 1': 'hexagonal',
                'hexagonal 2': 'hexagonal',
                'orthorhombic': 'soft',
                'orthorhombic base centred': 'soft',
                'orthorhombic body centred': 'soft',
                'orthorhombic face centred': 'soft',
                'rhombohedral': 'latticevectors',
                'simple cubic': 'soft',
                'simple monoclinic': 'latticevectors',
                'tetragonal': 'soft',
                'tetragonal base centred': 'soft',
                'tetragonal body centred': 'soft',
                'tetragonal face centred': 'soft',
                'triclinic': 'latticevectors'}


def reciprocal(a1, a2, a3, h, k, l, r_min, r_max):
    """
    Creates the reciprocal lattice and a given family of lattice planes.
    """
    # First the scaling factor for the reciprocal lattice
    scale = a1.dot(np.cross(a2, a3))
    # Then the reciprocal lattice
    b1 = 2 * np.pi * np.cross(a2, a3) / scale
    b2 = 2 * np.pi * np.cross(a3, a1) / scale
    b3 = 2 * np.pi * np.cross(a1, a2) / scale
    # And the normal vector for the (hkl)-family of planes.
    G = h * b1 + k * b2 + l * b3
    G_unit = G / mag(G)

    # Next the displacement vector d
    d = 2 * np.pi * G_unit / mag(G)

    # The vertical displacement of the planes (dz) is given by
    # mag(d)/cos(theta), where theta is the angle between the displacement
    # vector and the z-axis. cos(theta) is also d[2]/mag(d) (cosine of angle
    # between d and [0,0,1]):
    dz = mag(d)**2 / d[2]

    # We take the origin as the fix-point for the starting plane, then we just
    # create copies of this plane, displaced vertically by dz, until the top of
    # the first plane doesn't reach the bottom of the plot box, and the bottom
    # of the last plane doesn't reach the top of the plot box. But first we
    # create the meshgrid needed
    x = np.linspace(r_min[0], r_max[0])
    y = np.linspace(r_min[1], r_max[1])
    xv, yv = np.meshgrid(x, y)

    # Now the starting plane
    zv = (-d[0] * xv - d[1] * yv) / d[2]

    # The distance between the bottom of the plane and the max z-value
    delta_z_plus = r_max[2] - np.amin(zv)
    # The negative distance between the top of the plane and the min z-value
    delta_z_minus = r_min[2] - np.amax(zv)

    # The amount of planes needed in each direction to cover the plot box:
    nz_plus = np.ceil(delta_z_plus / dz)
    nz_minus = np.floor(delta_z_minus / dz)

    # Create a list of the planes with a list comprehension
    planes = [zv + n * d for n in range(nz_minus, nz_plus + 1)]

    return b1, b2, b3, d, planes


def generator(a1, a2, a3, basis, colors, sizes, lim_type, n_min, n_max,
              r_min, r_max, n_basis, grid_type=None, verbose=False):
    """
    Generates the atomic positions of the lattice, from the lattice- and basis-
    vectors
    """
    size_default = 36
    # Calculate the amount of atomic positions to be calculated
    num_atoms = ((n_max[0] + 1 - n_min[0]) * (n_max[1] + 1 - n_min[1]) *
                 (n_max[2] + 1 - n_min[2]) * n_basis)

    # Make a zero array for all of the atomic positions. num_atoms in one
    # direction and 3 in the other (coordinates)
    atomic_positions = np.zeros((num_atoms, 3))
    lattice_coefficients = np.zeros((num_atoms, 3))
    # Empty lists for colors, sizes and whether or not they're lattice points
    atomic_colors = []
    atomic_sizes = []
    lattice_position = []

    # Loop over all chosen linear combinations of basis vectors and plot each
    counter = 0
    for nx in range(n_min[0], n_max[0] + 1):
        for ny in range(n_min[1], n_max[1] + 1):
            for nz in range(n_min[2], n_max[2] + 1):
                lattice_coefficients[counter, ] = np.array([nx, ny, nz]).T
                position = nx * a1 + ny * a2 + nz * a3
                for n_atom in range(n_basis):
                    atomic_positions[counter, ] = (position +
                                                   basis[n_atom, ])
                    atomic_colors.append(colors[n_atom])
                    atomic_sizes.append(size_default * sizes[n_atom])

                    if (atomic_positions[counter, ] == position).all():
                        lattice_position.append(True)
                    else:
                        lattice_position.append(False)
                    counter += 1
    # Another way to do this is to use itertools.product to create all
    # permutations of -2, ..., 4 with repeat of 3, and then use np.asarray() to
    # convert this into a numpy array. The "problem" is that this doesn't allow
    # one to have nx_max = / = ny_max, etc. All ranges must be equal.
    # I should check to see which is fastest.
    # Strike that above problem. Just pass it a list for each coordinate with
    # the range and use no repeat.
    # atomic_coefficients = np.asarray(list(itertools.product(x, y, z)))
    # Where x, y, z is list of integers from nx_min to nx_max etc.
    # This would yield list of coefficients (nx, ny, nz), then we just multiply
    # the first dimension by a1, the second by a2 and so on. But not now

    # For some reason, we need to prune the coordinates again...
    atomic_positions[eq(atomic_positions, 0)] = 0

    if verbose:
        print("Unpruned Atomic Positions")
        print(atomic_positions)

    # Delete all elements that are outside
    objects = [atomic_positions, lattice_coefficients, atomic_colors,
               atomic_sizes, lattice_position]
    objects = limiter(atomic_positions, objects, r_min, r_max)

    if verbose:
        print("Pruned Atomic Positions")
        print(atomic_positions)
        print("r_min, r_max, n_min, n_max")
        print(r_min, r_max, n_min, n_max)

    return (atomic_positions, lattice_coefficients, atomic_colors,
            atomic_sizes, lattice_position)


def mag(a):
    """
    Returns magnitude of vector or each row of an array
    """
    # Return magnitude of vector
    if len(a.shape) == 1:
        return np.linalg.norm(a)
    # Return magnitude of each row of an array.
    else:
        return np.linalg.norm(a, axis=1)


def classifier(a1, a2, a3, basis):
    """
    test all bravais lattice types (primitive unit cells for all, conventional
    for fcc and bcc). It works by first checking how many of the lattice
    vectors have an equal magnitude, and then checking the angles between the
    lattice vectors. The angles are checked below with the extensive amount of
    boolean values.
    """

    # Create a lattice array and get the magnitude of the lattice vectors
    lattice = np.array([a1, a2, a3])
    mag_lattice = mag(lattice)
    mag_a1, mag_a2, mag_a3 = mag_lattice

    # Angles between lattice vectors
    cos12 = a1.dot(a2) / (mag_a1 * mag_a2)
    cos31 = a1.dot(a3) / (mag_a1 * mag_a3)
    cos23 = a2.dot(a3) / (mag_a2 * mag_a3)

    # bool of equality between lattice vector magnitudes
    mag12_eq = eq(mag_a1, mag_a2)
    mag31_eq = eq(mag_a1, mag_a3)
    mag23_eq = eq(mag_a2, mag_a3)

    # If all magnitudes are equal, then there's equality between all magnitudes
    mag_all_eq = mag12_eq and mag31_eq and mag23_eq

    # We check each of the permutations where only 1 pair is equal to each
    # other in magnitude
    mag_only_12_eq = (mag12_eq and (not mag31_eq) and (not mag23_eq))
    mag_only_31_eq = (mag31_eq and (not mag12_eq) and (not mag23_eq))
    mag_only_23_eq = (mag23_eq and (not mag31_eq) and (not mag12_eq))
    # XOR the above permutations together to make sure only one is true
    mag_only2eq = mag_only_12_eq ^ mag_only_31_eq ^ mag_only_23_eq

    # Check for orthogonality
    ortho12 = eq(0, np.dot(a1, a2))
    ortho31 = eq(0, np.dot(a1, a3))
    ortho23 = eq(0, np.dot(a2, a3))

    # all are orthogonal
    ortho = ortho12 and ortho31 and ortho23

    # only two pairs are orthogonal
    ortho2 = ((ortho12 and ortho31) ^ (ortho12 and ortho23) ^
              (ortho31 and ortho23))

    # The three possible permutations for hexagonal lattice. Hexagonal can both
    # have 3 equal sides or only two
    hexa3 = eq(0.5, cos12) and eq(0, cos31) and eq(0, cos23)
    hexa2 = eq(0.5, cos31) and eq(0, cos23) and eq(0, cos12)
    hexa1 = eq(0.5, cos23) and eq(0, cos12) and eq(0, cos31)
    hexa = hexa1 ^ hexa2 ^ hexa3

    fcc = eq(0.5, cos12) and eq(0.5, cos31) and eq(0.5, cos23)

    # rhombohedral have all angles equal to each other, but is not fcc
    rhombo = (eq(cos12, cos31) and eq(cos12, cos23) and
              eq(cos31, cos23) and not fcc)

    # the three bcc permutations available
    bcc3 = (eq(0, cos12) and eq(np.sqrt(3) / 3, cos31) and
            eq(np.sqrt(3) / 3, cos23))
    bcc2 = (eq(0, cos31) and eq(np.sqrt(3) / 3, cos23) and
            eq(np.sqrt(3) / 3, cos12))
    bcc1 = (eq(0, cos23) and eq(np.sqrt(3) / 3, cos12) and
            eq(np.sqrt(3) / 3, cos31))
    bcc = bcc1 ^ bcc2 ^ bcc3

    # The three tetragonal body centred permutations
    tbc3 = eq(0, cos12) and eq(cos23, cos31) and eq(cos23, mag_a2 /
                                                    (2 * mag_a3))
    tbc2 = eq(0, cos31) and eq(cos12, cos23) and eq(cos12, mag_a1 /
                                                    (2 * mag_a2))
    tbc1 = eq(0, cos23) and eq(cos31, cos12) and eq(cos31, mag_a3 /
                                                    (2 * mag_a1))
    tbc = tbc1 ^ tbc2 ^ tbc3

    # The three tetragonal face centred permutations
    tfc1 = (eq(cos12, cos31) and eq(cos12, mag_a1 / (2 * mag_a2)) and
            eq(cos23, (2 * mag_a2**2 - mag_a1**2) / (2 * mag_a3**2)))
    tfc2 = (eq(cos31, cos23) and eq(cos31, mag_a3 / (2 * mag_a1)) and
            eq(cos12, (2 * mag_a1**2 - mag_a3**2) / (2 * mag_a2**2)))
    tfc3 = (eq(cos23, cos12) and eq(cos23, mag_a2 / (2 * mag_a3)) and
            eq(cos31, (2 * mag_a3**2 - mag_a2**2) / (2 * mag_a1**2)))
    tfc = tfc1 ^ tfc2 ^ tfc3

    # Tetragonal base centred
    tbase3 = eq(cos12, np.sqrt(2) / 2) and eq(cos31, cos23) and eq(0, cos23)
    tbase2 = eq(cos31, np.sqrt(2) / 2) and eq(cos23, cos12) and eq(0, cos12)
    tbase1 = eq(cos23, np.sqrt(2) / 2) and eq(cos12, cos31) and eq(0, cos31)
    tbase = tbase1 ^ tbase2 ^ tbase3

    # Base centred monoclinic has 6 different permutations, and can have either
    # no sides equal, two sides equal or all sides equal. With two or three
    # sides equal it has a 2D triangular lattice, where each 2D lattice is
    # displaced with respect to the other.
    base_mono_3 = (eq(cos12, mag_a1 / (2 * mag_a2)) and
                   eq(cos23, a1.dot(a3) / (2 * mag_a2 * mag_a3)))
    base_mono_2 = (eq(cos31, mag_a3 / (2 * mag_a1)) and
                   eq(cos12, a3.dot(a2) / (2 * mag_a1 * mag_a2)))
    base_mono_1 = (eq(cos23, mag_a2 / (2 * mag_a3)) and
                   eq(cos31, a2.dot(a1) / (2 * mag_a3 * mag_a1)))
    base_mono_4 = (eq(cos31, mag_a1 / (2 * mag_a3)) and
                   eq(cos23, a1.dot(a2) / (2 * mag_a3 * mag_a2)))
    base_mono_5 = (eq(cos23, mag_a3 / (2 * mag_a2)) and
                   eq(cos12, a3.dot(a1) / (2 * mag_a2 * mag_a1)))
    base_mono_6 = (eq(cos12, mag_a2 / (2 * mag_a1)) and
                   eq(cos31, a2.dot(a3) / (2 * mag_a1 * mag_a3)))
    base_mono = (base_mono_1 ^ base_mono_2 ^ base_mono_3 ^
                 base_mono_4 ^ base_mono_5 ^ base_mono_6)

    # Orthorhombic body centred
    obc1 = (eq(cos12, 0) and eq(cos31, mag_a1 / (2 * mag_a3)) and
            eq(cos23, mag_a2 / (2 * mag_a3)))
    obc2 = (eq(cos31, 0) and eq(cos23, mag_a3 / (2 * mag_a2)) and
            eq(cos12, mag_a1 / (2 * mag_a2)))
    obc3 = (eq(cos23, 0) and eq(cos12, mag_a2 / (2 * mag_a1)) and
            eq(cos31, mag_a3 / (2 * mag_a1)))
    obc = obc1 ^ obc2 ^ obc3

    # Just need one here. Permutations lead to the exact same expression
    ofc = (eq(cos12, (mag_a1**2 + mag_a2**2 - mag_a3**2) /
                     (2 * mag_a1 * mag_a2)) and
           eq(cos23, (-mag_a1**2 + mag_a2**2 + mag_a3**2) /
                     (2 * mag_a2 * mag_a3)) and
           eq(cos31, (mag_a1**2 - mag_a2**2 + mag_a3**2) /
                     (2 * mag_a3 * mag_a1)))

    # obase False positives base_mono, since the dot product in the
    # angle formulas all give 0
    # Again we have 6 possible permutations
    obase1 = eq(cos12, mag_a1 / (2 * mag_a2)) and ortho23 and ortho31
    obase2 = eq(cos31, mag_a3 / (2 * mag_a1)) and ortho12 and ortho23
    obase3 = eq(cos23, mag_a2 / (2 * mag_a3)) and ortho31 and ortho12
    obase4 = eq(cos23, mag_a3 / (2 * mag_a2)) and ortho12 and ortho31
    obase5 = eq(cos31, mag_a1 / (2 * mag_a3)) and ortho23 and ortho12
    obase6 = eq(cos12, mag_a2 / (2 * mag_a1)) and ortho31 and ortho23
    obase = obase1 ^ obase2 ^ obase3 ^ obase4 ^ obase5 ^ obase6

    # Triclinic has no angles equal
    tri = ((not eq(cos12, cos23)) and (not eq(cos23, cos31)) and
           (not eq(cos31, cos12)))

    # We start with an undetermined lattice type
    lattice_type = "undetermined"
    if mag_all_eq:
        # Side lengths are equal. Lattice types:
        # Cubic,
        # rhombohedral,
        # face centered cubic,
        # hexagonal with a=|a_1|,
        # Tetragonal Body centered with b=+-sqrt(2)a
        # base centred monoclinic, b = +-sqrt(3)a, c = a
        # conventional fcc
        # conventional bcc
        if ortho:
            # Let's detect the conventional unit cells of fcc and bcc. Requires
            # more than one basis vector
            if len(basis.shape) == 1:
                lattice_type = "simple cubic"
            else:
                # we exclude the first basis vector ([0,0,0])
                reduced_basis = basis[1:]
                mag_basis = mag(reduced_basis)
                # bcc has one basis vector in the reduced basis
                if reduced_basis.shape[0] == 1:
                    # Make sure the reduced basis is a vector
                    reduced_basis = reduced_basis.flatten()
                    # check if the vector has the right length
                    length_eq = eq(np.sqrt(3) / 2, mag_basis / mag_a1)
                    # calculate angles
                    angles = lattice.dot(reduced_basis) / (mag_basis * mag_a1)
                    # make sure the angles are all the right magnitude
                    angles_eq = np.all(eq(angles, np.sqrt(3) / 3))
                    # if lengths and angles are correct, it's bcc
                    if length_eq and angles_eq:
                        lattice_type = "conventional bcc"

                # fcc has 3 basis vectors in the reduced basis
                elif reduced_basis.shape[0] == 3:
                    # check if all length ratios are sqrt(2)/2
                    length_eq = eq(np.sqrt(2) / 2, mag_basis / mag_a1).all()

                    # Calculate angles between lattice vectors and basis
                    # vectors
                    normalizer = np.outer(mag_lattice, mag_basis)
                    angles = lattice.dot(reduced_basis) / normalizer
                    # Calculate rank of matrix
                    rank = np.linalg.matrix_rank(angles)

                    # get angles that are sqrt(2)/2 and 0 respectively
                    num_sqrt2 = eq(angles, np.sqrt(2) / 2)
                    num_0 = eq(angles, 0)

                    # Check whether there are 2 or 1 of these per row
                    # respectively
                    num_sqrt2_true = (num_sqrt2.sum(axis=1) ==
                                      np.array([2, 2, 2])).all()
                    num_0_true = (num_0.sum(axis=1) ==
                                  np.array([1, 1, 1])).all()
                    angles_eq = rank == 3 and num_0_true and num_sqrt2_true
                    if length_eq and angles_eq:
                        lattice_type = "conventional fcc"

        elif hexa:
            lattice_type = "hexagonal 1"
        elif fcc:
            lattice_type = "fcc"
        elif tbc:
            lattice_type = "tetragonal body centred"
        elif base_mono:
            lattice_type = "base centred monoclinic 1"
        elif rhombo:
            lattice_type = "rhombohedral"
        else:
            pass

    elif mag_only2eq:
        # Only two lengths are equal. Possible lattices
        # BCC
        # Tetragonal bc
        # tetragonal fc
        # tetragonal cubic
        # Cubic Base Centered
        # Base centered monoclinic (b=+-sqrt(3) * a)
        # Hexagonal
        # simple monoclinic, a=b or a=c or b=c
        if bcc:
            lattice_type = "bcc"
        # tbc actually gives a false positive for regular bcc.
        elif tbc:
            lattice_type = "tetragonal body centred"
        elif tfc:
            lattice_type = "tetragonal face centred"
        elif tbase:
            lattice_type = "base centred cubic"
        elif ortho:
            lattice_type = "tetragonal"
        elif hexa:
            lattice_type = "hexagonal 2"
        elif base_mono:
            lattice_type = "base centred monoclinic 2"
        elif ortho2:
            lattice_type = "simple monoclinic"
        else:
            pass
    else:
        # no side lengths are equal. Possible lattices:
        # Orthorhombic
        # OBC
        # OFC
        # Orthorhombic base centered
        # Tetragonal base centered (primitive), b != a and b != sqrt(2)a
        # Simple Monoclinic
        # Base centered Monoclinic
        # Triclinic
        if ortho:
            lattice_type = "orthorhombic"
        elif obc:
            lattice_type = "orthorhombic body centred"
        elif ofc:
            lattice_type = "orthorhombic face centred"
        elif tbase:
            lattice_type = "tetragonal base centred"
        elif obase:
            lattice_type = "orthorhombic base centred"
        elif base_mono:
            lattice_type = "base centred monoclinic 3"
        elif ortho2:
            lattice_type = "simple monoclinic"
        elif tri:
            lattice_type = "triclinic"
        else:
            pass
    return lattice_type


def rot_matrix(v=np.array([1, 1, 1]), theta=np.pi / 4):
    """
    Generates the rotation matrix for rotation about a given vector with a
    given angle. See https://en.wikipedia.org/wiki/Rotation_matrix
    """
    # Make sure we have a unit vector
    if (v == 0).all():
        print("You tried to rotate around the null-vector!")
    v = v / mag(v)
    # Create the cross product matrix
    v_cross = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    # Tensor product
    v_tens = np.tensordot(v, v, 0)
    # Return rotation matrix
    return (np.cos(theta) * np.identity(3) + np.sin(theta) *
            v_cross + (1 - np.cos(theta)) * v_tens)


def chooser(lattice_name="simple cubic", verbose=False):
    """
    Outputs the chosen lattice and basis
    """
    # Let's just sanitize the input
    lattice_name = lattice_name.lower()
    L = {}
    B = {}
    a, b, c, theta = 1, 1.5, 2, 80 * np.pi / 180
    # Create the relevant lattices (transposed - using row vectors)
    # Simple cubic
    lcubic = np.array([[a, 0, 0], [0, a, 0], [0, 0, a]])
    L["simple cubic"] = lcubic
    # BCC
    lbcc = np.array([[a, 0, 0], [0, a, 0], [a / 2, a / 2, a / 2]])
    L["bcc"] = lbcc
    # FCC
    lfcc = np.array([[a / 2, a / 2, 0], [a / 2, 0, a / 2], [0, a / 2, a / 2]])
    L["fcc"] = lfcc
    # Base Centered Cubic
    lcbase = np.array([[a, 0, 0], [a / 2, a / 2, 0], [0, 0, a]])
    L["base centred cubic"] = lcbase
    # Tetragonal
    ltetra = np.array([[a, 0, 0], [0, a, 0], [0, 0, b]])
    L["tetragonal"] = ltetra
    # Tetragonal Body Centred
    ltbc = np.array([[a, 0, 0], [0, a, 0], [a / 2, a / 2, b / 2]])
    L["tetragonal body centred"] = ltbc
    # Tetragonal Face Centred
    ltfc = np.array([[a / 2, a / 2, 0], [a / 2, 0, b / 2], [0, a / 2, b / 2]])
    L["tetragonal face centred"] = ltfc
    # tetragonal base centred
    ltbase = np.array([[a, 0, 0], [a / 2, a / 2, 0], [0, 0, b]])
    L["tetragonal base centred"] = ltbase
    # Orthorhombic
    lortho = np.array([[a, 0, 0], [0, b, 0], [0, 0, c]])
    L["orthorhombic"] = lortho
    # Orthorhombic body centred
    lobc = np.array([[a, 0, 0], [0, b, 0], [a / 2, b / 2, c / 2]])
    L["orthorhombic body centred"] = lobc
    # Orthorhombic Face centred
    lofc = np.array([[a / 2, b / 2, 0], [a / 2, 0, c / 2], [0, b / 2, c / 2]])
    L["orthorhombic face centred"] = lofc
    # Orthorhombic base centred
    lobase = np.array([[a, 0, 0], [a / 2, b / 2, 0], [0, 0, c]])
    L["orthorhombic base centred"] = lobase
    # simple monoclic
    lsmono = np.array([[a, 0, 0], [0, b, 0],
                       [c * np.cos(theta), 0, c * np.sin(theta)]])
    L["simple monoclinic"] = lsmono
    # base centred monoclinic
    lbcmono = np.array([[a, 0, 0], [a / 2, b / 2, 0],
                        [c * np.cos(theta), 0, c * np.sin(theta)]])
    L["base centred monoclinic"] = lbcmono
    # Base centred monoclinic (2)
    lbcmono2 = np.array([[a, 0, 0], [a / 2, np.sqrt(3) * a / 2, 0],
                         [c * np.cos(theta), 0, c * np.sin(theta)]])
    L["base centred monoclinic 2"] = lbcmono2
    # Base centred monoclinic (3)
    lbcmono3 = np.array([[a, 0, 0], [a / 2, np.sqrt(3) * a / 2, 0],
                         [a * np.cos(theta), 0, a * np.sin(theta)]])
    L["base centred monoclinic 1"] = lbcmono3
    # Hexagonal 1
    lhexa1 = np.array([[a, 0, 0], [a / 2, np.sqrt(3) * a / 2, 0], [0, 0, a]])
    L["hexagonal"] = lhexa1
    # Hexagonal 2
    lhexa2 = np.array([[a, 0, 0], [a / 2, np.sqrt(3) * a / 2, 0], [0, 0, b]])
    L["hexagonal 2"] = lhexa2
    # Triclinc stuff
    gamma = 70 * np.pi / 180
    beta = 60 * np.pi / 180
    cx = c * np.cos(beta)
    cy = c * (np.cos(theta) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma)
    cz = np.sqrt(c**2 - cx**2 - cy**2)
    ltri = np.array([[a, 0, 0], [b * np.cos(gamma), b * np.sin(gamma), 0],
                     [cx, cy, cz]])
    L["triclinic"] = ltri
    # Rhombohedral
    lrhombo = np.array([[a, b, b], [b, a, b], [b, b, a]])
    L["rhombohedral"] = lrhombo

    # conventional fcc
    L["conventional fcc"] = lcubic
    B["conventional fcc"] = a * np.array([[0.5, 0.5, 0],
                                          [0.5, 0, 0.5],
                                          [0, 0.5, 0.5]])

    L["conventional bcc"] = lcubic
    B["conventional bcc"] = a * np.array([0.5, 0.5, 0.5])

    # Diamond lattice
    L["diamond"] = lfcc
    B["diamond"] = a * np.array([0.25, 0.25, 0.25])

    # Zinc-blende
    L["zincblende"] = L["diamond"]
    B["zincblende"] = B["diamond"]

    # Wurtzite
    u = 3 / 8
    L["wurtzite"] = np.array([[0.5 * a, -a * np.sqrt(3) / 2, 0],
                              [0.5 * a, a * np.sqrt(3) / 2, 0], [0, 0, b]])
    B["wurtzite"] = np.array([[0, -a * np.sqrt(3) / 3, b / 2],
                              [0, 0, u * b],
                              [0, -a * np.sqrt(3) / 3, (1 / 2 + u) * b]])

    try:
        lattice = L[lattice_name]
    except KeyError:
        print("You did da dumdum, and I now give you simple cubic")
        lattice = L["simple cubic"]

    basis_origin = np.array([0, 0, 0])

    try:
        basis = B[lattice_name]
    except KeyError:
        basis = np.array([])

    if basis.shape[0] > 0:
        basis = np.vstack((basis_origin, basis))
    elif basis.shape[0] == 0:
        basis = np.hstack((basis_origin, basis))
    else:
        print("something went horribly wrong")

    if verbose:
        print("Returning the following lattice and basis")
        print(lattice)
        print(basis)
    return lattice, basis


def tester(verbose=False):
    """
    Tests all the lattices for lattice detection, with permutations and
    rotations
    """
    # List of all the lattices
    lattices = ["simple cubic", "fcc", "bcc", "conventional fcc",
                "conventional bcc", "base centred cubic", "tetragonal",
                "tetragonal body centred", "tetragonal face centred",
                "tetragonal base centred", "orthorhombic",
                "orthorhombic base centred", "orthorhombic body centred",
                "orthorhombic face centred", "simple monoclinic",
                "base centred monoclinic", "base centred monoclinic 2",
                "base centred monoclinic 3", "hexagonal", "hexagonal 2",
                "triclinic", "rhombohedral"]

    # Create the rotation matrix
    R = rot_matrix()
    for name in lattices:
        # Create the lattice
        lattice, basis = chooser(name, verbose=verbose)
        # rotate the lattice and basis
        lattice = (R@lattice.T).T
        basis = (R@basis.T).T
        for perm in itertools.permutations([0, 1, 2]):
            # permute the lattice
            a1, a2, a3 = lattice[list(perm)]

            # next we classify it
            lattice_type = classifier(a1, a2, a3, basis)

            if verbose:
                print("Lattice: {}. Classification: {}. Permutation {}".format(
                      name,
                      lattice_type,
                      perm))
            else:
                if name != lattice_type:
                    s = "L: {}, C: {}, P: {}".format(name, lattice_type, perm)
                    print(s)
    if verbose:
        print("Test done.")
    else:
        print("Test done. If nothing printed, all were succesfully classified")


def find_limits(lim_type, a1, a2, a3, min_=[0, 0, 0], max_=[2, 2, 2]):
    """
    Calculates the limits on the coordinates (the plot box), and the limits on
    the basis vector ranges.
    """
    n_min, n_max = np.array(min_), np.array(max_)
    lattice = np.array((a1, a2, a3))
    # For dynamic limits we pass min_ and max_ as limits of basis vector range
    # and calculate coordinate limit based on basis vector range
    if lim_type.lower() in "individual":
        # Take the max value for each of the cardinal directions, for the
        # three scaled lattice vectors (so x_max is max x value of
        # max_[0] * a1, max_[1] * a2 and max_[2] * a3).
        # this can be done by multiplying the transposed lattice matrix by the
        # n_max vector, then taking max value
        max_vects = lattice.T * n_max
        r_max = np.amax(max_vects, 0)
        # Similar for minimums:
        min_vects = lattice.T * n_min
        r_min = np.amin(min_vects, 0)
    # Different type of coordinate limits. Take r_max as sum(lattice * max)
    # Works well for orthogonal or near-orthogonal lattice vectors
    elif lim_type.lower() in "sum":
        r_max = np.sum(lattice.T * n_max, 0)
        r_min = np.sum(lattice.T * n_min, 0)
    elif lim_type.lower() in "proper":
        # We sample all 8 points arising from combinations of min and max:
        # First we get the permutations:
        perms = list(itertools.product([False, True], repeat=3))
        # We create a boolean array of when to multiply by the max and when not
        # to
        max_mult = np.array(perms)
        min_mult = np.invert(max_mult)
        # We stack the min and max arrays to have 8 identical rows
        max_stack = np.array(max_ * 8).reshape([8, 3])
        min_stack = np.array(min_ * 8).reshape([8, 3])
        # Each element of the multiplier matrix is made of the appropriate
        # element from max or min. If max_mult[n,m] == False then mult[n,m] =
        # min_stack[n,m] and vice versa. This is accomplished by setting the
        # elements of max_stack and min_stack equal to 0, when they are not to
        # be multiplied. Then we add the two arrays together.
        max_stack[min_mult] = 0
        min_stack[max_mult] = 0
        mult = min_stack + max_stack
        # The 8 points are thus the matrix product of mult and lattice
        limits = mult @ lattice
        # We take the minimal and maximal values of each column, as the minimum
        # and maximum value for our cartesian axes
        r_min = np.amin(limits, 0)
        r_max = np.amax(limits, 0)
    else:
        print('You chose... poorly.')
    # And lastly we return the relevant arrays, with n_min / max -+ some value
    # to allow for "spillage". The value is the maximal value of the max_
    # array. Also, let's make sure n_min / max are arrays of integers. Don't
    # worry, they've already been rounded
    returns = (r_min, r_max, n_min.astype('int') - np.max(max_),
               n_max.astype('int') + np.max(max_))
    return returns


def limiter(l, objects, r_min=np.array([0, 0, 0]), r_max=np.array([2, 2, 2])):
    """
    A function to highlight points that are outside the limits of the plot
    """
    num, _ = np.shape(l)
    # loop over all row IDs. Add the row ID to the list if all coordinates of
    # the corresponding point are smaller than those of r_min, or larger than
    # those of r_max

    rows = [row_id for row_id in range(num) if
            ((r_min > l[row_id, ]).any() or (l[row_id, ] > r_max).any())]

    limited_objects = []
    for object_ in objects:
        name = object_.__class__.__name__
        if name == 'ndarray':
            limited_objects.append(np.delete(object_, rows, 0))
        if name == 'list':
            for ID in sorted(rows, reverse=True):
                del object_[ID]
            limited_objects.append(object_)

    return limited_objects


def rotate_face_centred(a1, a2, a3, basis, verbose=False):
    """
    Rotation function for face centred lattices
    """
    ma1 = a1.dot(a1)
    ma2 = a2.dot(a2)
    ma3 = a3.dot(a3)

    # First we get the relevant lengths:
    a = np.sqrt(2 * (ma1 + ma2 - ma3))
    b = np.sqrt(2 * (ma1 - ma2 + ma3))
    c = np.sqrt(2 * (-ma1 + ma2 + ma3))

    # And now the "proper" lattice vectors
    a1_prop = np.array([a / 2, b / 2, 0])
    a2_prop = np.array([a / 2, 0, c / 2])
    a3_prop = np.array([0, b / 2, c / 2])

    # Now we align a1 with a1_prop:
    a1_cross = np.cross(a1, a1_prop)
    if eq(0, mag(a1_cross)):
        pass
    else:
        theta = np.arcsin(mag(a1_cross) / (mag(a1) * mag(a1_prop)))
        r1 = rot_matrix(a1_cross, theta)
        a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

        # And of course check that we've rotated correctly
        if eq(a1, a1_prop).all():
            pass
        else:
            r1 = rot_matrix(a1_cross, -2 * theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

    # Next we align a2 with a2_prop:
    theta, r2 = rot_matrix_along(a1_prop, a2, a2_prop)
    a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)
    if eq(a2, a2_prop).all():
        # We rotated properly!
        pass
    else:
        # Rotate the other way
        r2 = rot_matrix(a1_prop, -2 * theta)
        a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

    # To be sure, let's see if a3 and a3_prop are (anti)parallel:
    cos3 = a3.dot(a3_prop) / (mag(a3) * mag(a3_prop))
    if verbose:
        if eq(cos3, 1):
            print("a3 and a3_prop are parallel")
        elif eq(cos3, -1):
            print("a3 and a3_prop are ANTIparallel")
        else:
            print("a3 and a3_prop are neither parallel or antiparallel. Check!"
                  )

    return a1, a2, a3, basis


def rotate_bcm(a1, a2, a3, basis):
    """
    rotation function for base centred monoclinic. Rotates the lattice such
    that a1 is along x, and a2 is in the xy-plane
    """
    x = np.array([1, 0, 0])
    y = np.array([0, 1, 0])

    # We align a1 along x
    a1_cross = np.cross(a1, x)
    if eq(0, mag(a1_cross)):
        pass
    else:
        theta = np.arcsin(mag(a1_cross) / mag(a1))
        r1 = rot_matrix(a1_cross, theta)
        a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

    # Get the rotation matrix to align a2 in the xy plane (vector rejection
    # parallel to y)
    theta, r2 = rot_matrix_along(a1, a2, y)
    a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

    # Make sure a2 is perpendicular to z
    if eq(a2[2], 0):
        pass
    else:
        # rotate the other way!
        r2 = rot_matrix(a1, -2 * theta)
        a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

    return a1, a2, a3, basis


def rot_matrix_along(a, b, c):
    """
    creates the rotation matrix which rotates b about a, such that its vector
    rejection coincides with that of c
    """

    # First we need the relevant vector rejections
    brej = b - b.dot(a) / (mag(a)**2) * a
    crej = c - c.dot(a) / (mag(a)**2) * a

    # Next we get the angle between the rejections
    theta = np.arccos(brej.dot(crej) / (mag(brej) * mag(crej)))
    # and the relevant rotation matrix
    R = rot_matrix(a, theta)
    return theta, R


def rotate_hex(a1, a2, a3, basis):
    """
    Rotator for the hexagonal structure
    """
    mag_a1 = mag(a1)
    mag_a2 = mag(a2)
    mag_a3 = mag(a3)
    cos12 = a1.dot(a2) / (mag_a1 * mag_a2)
    cos31 = a1.dot(a3) / (mag_a1 * mag_a3)
    cos23 = a2.dot(a3) / (mag_a2 * mag_a3)
    x = np.array([1, 0, 0])
    z = np.array([0, 0, 1])

    # Rotate the lattice according to which vectors form the triangular lattice
    if eq(0.5, cos12):
        # a1 and a2 form triangular lattice. Align a1 along x
        a1_cross = np.cross(a1, x)
        if eq(0, mag(a1_cross)):
            # We are already rotated.
            pass
        else:
            theta = np.arcsin(mag(a1_cross) / mag_a1)
            r1 = rot_matrix(a1_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

        # now rotate a3 so it's parallel to z, with x as rotation axis
        theta = np.arccos(a3.dot(z) / (mag_a3))
        if eq(0, theta):
            # We're already properly rotated for a3 as well.
            r3 = rot_matrix(x, theta)
            A1, A2, A3, Basis = rotate(a1, a2, a3, basis, r3)
            # Alright, so I don't know how to get the proper rotation
            # direction, so we just check if it's rotated properly
            if eq(A2[2], 0):
                # We rotated correctly
                a1, a2, a3, basis = A1, A2, A3, Basis
            else:
                # We didn't rotate correctly, so we rotate the other way
                r3 = rot_matrix(x, -theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)

    elif eq(0.5, cos23):
        # a2 and a3 form triangular lattice. Align a2 along x
        a2_cross = np.cross(a2, x)
        if eq(0, mag(a2_cross)):
            # We've already rotated
            pass
        else:
            theta = np.arcsin(mag(a2_cross) / mag_a2)
            r2 = rot_matrix(a2_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

        # now rotate a1 so it's parallel to z, with x as rotation axis
        theta = np.arccos(a1.dot(z) / (mag_a1))
        if eq(0, theta):
            pass
        else:
            r1 = rot_matrix(x, theta)
            A1, A2, A3, Basis = rotate(a1, a2, a3, basis, r1)
            # Alright, so I don't know how to get the proper rotation
            # direction, so we just check if it's rotated properly It's rotated
            # properly if the z-coordinate of A3 is 0. Also, we return the
            # lattice vectors, such that a1 and a2 form the triangular lattice
            if eq(A3[2], 0):
                # We rotated correctly
                a1, a2, a3, basis = A1, A2, A3, Basis
            else:
                # We didn't rotate correctly, so we rotate the other way
                r1 = rot_matrix(x, -theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

    elif eq(0.5, cos31):
        # a1 and a3 form triangular lattice. Align a1 along x
        a1_cross = np.cross(a1, x)
        if eq(0, mag(a1_cross)):
            pass
        else:
            theta = np.arcsin(mag(a1_cross) / mag_a1)
            r1 = rot_matrix(a1_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

        # now rotate a2 so it's parallel to z, with x as rotation axis
        theta = np.arccos(a2.dot(z) / (mag_a2))
        if eq(0, theta):
            pass
        else:
            r2 = rot_matrix(x, theta)
            A1, A2, A3, Basis = rotate(a1, a2, a3, basis, r2)
            # Alright, so I don't know how to get the proper rotation
            # direction, so we just check if it's rotated properly. Also we
            # return the lattice vectors such that a1 and a2 form the
            # triangular lattice
            if eq(A3[2], 0):
                # We rotated correctly
                a1, a2, a3, basis = A1, A2, A3, Basis
            else:
                # We didn't rotate correctly, so we rotate the other way
                r3 = rot_matrix(x, -theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)
    else:
        print('something went wrong rotating the hexagonal lattice')

    return a1, a2, a3, basis


def rotate(a1, a2, a3, basis, R):
    """
    Rotates the whole lattice given the rotation matrix.
    """
    return R@a1, R@a2, R@a3, (R@basis.T).T


def parallel(a1, a2):
    """
    returns True if vectors are (anti)parallel and false if they're not
    """
    mag1 = mag(a1)
    mag2 = mag(a2)
    cos12 = a1.dot(a2) / (mag1 * mag2)
    para = eq(1, cos12) or eq(-1, cos12)
    return para


def rotator(a1, a2, a3, basis, latticetype=None, verbose=False):
    """
    Rotates the lattice to make plotting gridlines easier
    """
    # We remember, that |a x b| = |a| |b| sin(theta)
    eq = np.isclose
    x = np.array([1, 0, 0])
    y = np.array([0, 1, 0])
    z = np.array([0, 0, 1])
    # Check for orthogonality
    ortho12 = eq(0, np.dot(a1, a2))
    ortho31 = eq(0, np.dot(a1, a3))
    ortho23 = eq(0, np.dot(a2, a3))
    face_centred = "face centred" in latticetype or latticetype == "fcc"

    if verbose:
        print("Before:")
        print(a1)
        print(a2)
        print(a3)
        print(basis)
        print("orthogonality")
        print(ortho12, ortho31, ortho23)

    if "hexagonal" in latticetype:
        a1, a2, a3, basis = rotate_hex(a1, a2, a3, basis)
    elif "base centred monoclinic" in latticetype:
        a1, a2, a3, basis = rotate_bcm(a1, a2, a3, basis)
    elif face_centred:
        a1, a2, a3, basis = rotate_face_centred(a1, a2, a3, basis, verbose)
    elif ortho12:
        # We choose a1 to align along x
        a1_cross = np.cross(a1, x)
        if eq(0, mag(a1_cross)):
            # We're already parallel!
            pass
        else:
            # We need to rotate!
            theta = np.arcsin(mag(a1_cross) / mag(a1))
            r1 = rot_matrix(a1_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

            if parallel(a1, x):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r1 = rot_matrix(a1_cross, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

        # Now we align a2 along y
        # But we gotta make sure we rotate in the right direction
        a2_cross = np.cross(a2, y)
        if eq(0, mag(a2_cross)):
            pass
        else:
            theta = np.arcsin(mag(a2_cross) / mag(a2))
            r2 = rot_matrix(x, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

            # Let's check that a2 is along y:
            if parallel(a2, y):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r2 = rot_matrix(x, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

    elif ortho31:
        # We choose a1 to align along x
        a1_cross = np.cross(a1, x)
        if eq(0, mag(a1_cross)):
            pass
        else:
            theta = np.arcsin(mag(a1_cross) / mag(a1))
            r1 = rot_matrix(a1_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

            if parallel(a1, x):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r1 = rot_matrix(a1_cross, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r1)

        # Now we align a3 along z
        a3_cross = np.cross(a3, z)
        if eq(0, mag(a3_cross)):
            pass
        else:
            theta = np.arcsin(mag(a3_cross) / mag(a3))
            r3 = rot_matrix(x, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)

            # Let's check that a3 is along y:
            if parallel(a3, z):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r3 = rot_matrix(x, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)

    elif ortho23:
        # We choose a2 to align along x
        a2_cross = np.cross(a2, x)
        if eq(0, mag(a2_cross)):
            pass
        else:
            theta = np.arcsin(mag(a2_cross) / mag(a2))
            r2 = rot_matrix(a2_cross, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

            if parallel(a2, y):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r2 = rot_matrix(x, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r2)

        # Now we align a3 along y
        a3_cross = np.cross(a3, y)
        if eq(0, mag(a3_cross)):
            pass
        else:
            theta = np.arcsin(mag(a3_cross) / mag(a3))
            r3 = rot_matrix(x, theta)
            a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)

            # Let's check that a3 is along y:
            if parallel(a3, y):
                pass
            else:
                # We rotated the wrong way! Let's rotate the other way twice
                r3 = rot_matrix(x, -2 * theta)
                a1, a2, a3, basis = rotate(a1, a2, a3, basis, r3)
    else:
        # Well, it doesn't really matter here, if none of them are orthogonal
        # to each other. We'll just use latticevector gridlines and leave this
        # be.
        pass

    # Let's sanitize the coordinates that are close to 0 (say if a1x =
    # 2*10^-10, then we set it equal 0)
    a1[eq(a1, 0)] = 0
    a2[eq(a2, 0)] = 0
    a3[eq(a3, 0)] = 0
    basis[eq(basis, 0)] = 0

    if verbose:
        print("after")
        print(a1)
        print(a2)
        print(a3)
        print(basis)

    return a1, a2, a3, basis


def create_línes(points, vectors):
    """
    Creates lines along vectors and limits these to the given plot box
    """

    # For each lattice point, we calculate the cosine of the angle between each
    # of the lattice vectors and each of the separation vectors to other
    # lattice points. This allows us to determine which atoms lie along a
    # lattice vector from a given point. Then we can just pick the atom
    # furthest away (in the "positive" direction), and use it as the end point
    # for the grid line.
    lines = []

    # Create all gridlines needed and append them to the lines-list
    num_points = np.shape(points)[0]
    for row_id in range(num_points):
        current_point = points[row_id, ]
        for vec in vectors:
            # First we want to delete the origin from the separation
            sep = points - current_point
            # We make a boolean array of values equal to 0, sum them up and if
            # a row equals 3, then it is the null vector
            naughts = np.sum((sep == np.array([0, 0, 0])), 1) == 3
            # Then we select all the separation vectors that are not the
            # nullvector
            not_naughts = np.invert(naughts)
            sep = sep[not_naughts]
            non_points = points[not_naughts]
            mag_sep = mag(sep)

            # We calculate the cosine of the angle between the current lattice
            # vector and the separation vectors
            cosine = sep.dot(vec) / (mag_sep * mag(vec))
            # If it is close to 1, then the vectors are parallel
            para = eq(1, cosine)
            # We get the parallel points and magnitude of parallel separation
            # vectors
            para_points = non_points[para, ]
            mag_para_sep = mag_sep[para]
            if mag_para_sep.shape[0] == 0:
                # if there are no points further out, that have a parallel
                # separation vector, we just pass, as we are at the edge of the
                # lattice
                pass
            else:
                # We pick the parallel point, that has the largest magnitude of
                # the separation vector
                end_point_bool = mag_para_sep == np.amax(mag_para_sep)
                end_point = para_points[end_point_bool]
                end_point = np.squeeze(end_point)
                raw_line = np.vstack((current_point, end_point))
                lines.append([raw_line[:, 0], raw_line[:, 1], raw_line[:, 2]])

    return lines


def grid_lines(a1, a2, a3, atomic_positions, lattice_position, grid_type,
               verbose=False):
    """
    Create gridlines based on the grid_type. Either along lattice vectors or
    the cartesian axes.
    """

    grid_type = grid_type.lower()
    lines = []

    if grid_type in "latticevectors":
        # gridlines along lattice vectors - really messy for non-orthogonal
        # latticevectors
        vectors = np.array([a1, a2, a3])
        lines = create_línes(atomic_positions[lattice_position], vectors)
    elif grid_type in "hexagonal":
        vectors = np.array([a1, a2, a3, a1 - a2])
        lines = create_línes(atomic_positions[lattice_position], vectors)
    elif grid_type in "soft":
        # A Way of finding atoms on cartesian axes
        # bool array of atoms with x = 0 and y = 0
        x0 = atomic_positions[:, 0] == 0
        y0 = atomic_positions[:, 1] == 0
        z0 = atomic_positions[:, 2] == 0

        # Get Lattice spacings
        # z-values of atoms on the z-axis
        z_vals = atomic_positions[x0 * y0, 2]
        # Keep those with z > 0
        absz_vals = np.abs(z_vals[z_vals > 0])
        # Take the minimum as the lattice spacing
        a_z = np.min(absz_vals)

        y_vals = atomic_positions[x0 * z0, 1]
        absy_vals = np.abs(y_vals[y_vals > 0])
        a_y = np.min(absy_vals)

        x_vals = atomic_positions[y0 * z0, 0]
        absx_vals = np.abs(x_vals[x_vals > 0])
        a_x = np.min(absx_vals)

        # x = np.array([a_x, 0, 0])
        # y = np.array([0, a_y, 0])
        # z = np.array([0, 0, a_z])

        # Get the maximal and minimal values
        xmax = np.amax(x_vals)
        xmin = np.amin(x_vals)
        ymax = np.amax(y_vals)
        ymin = np.amin(y_vals)
        zmax = np.amax(z_vals)
        zmin = np.amin(z_vals)

        if verbose:
            print("Atoms on cardinal axes")
            print(x_vals)
            print(y_vals)
            print(z_vals)
        range_x = np.arange(xmin, xmax + 0.5 * a_x, a_x)
        range_y = np.arange(ymin, ymax + 0.5 * a_y, a_y)
        range_z = np.arange(zmin, zmax + 0.5 * a_z, a_z)
        for nx in range_x:
            for ny in range_y:
                lines.append([np.array([nx, nx]),
                              np.array([ny, ny]),
                              np.array([zmin, zmax])])

            for nz in range_z:
                lines.append([np.array([nx, nx]),
                              np.array([ymin, ymax]),
                              np.array([nz, nz])])
        for ny in range_y:
            for nz in range_z:
                lines.append([np.array([xmin, xmax]),
                              np.array([ny, ny]),
                              np.array([nz, nz])])
    else:
        print("No Gridlines Chosen")

    return lines
