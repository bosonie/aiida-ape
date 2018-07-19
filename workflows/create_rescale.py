from aiida.backends.utils import load_dbenv, is_dbenv_loaded
from aiida.work.workfunction import workfunction as wf
#from aiida.workflows2.wf import wf
if not is_dbenv_loaded():
    load_dbenv()
from aiida.orm import DataFactory

@wf
def structure_init(element):
    """
    Workfunction to create structure of a given element taking it from a reference
    list of scructures and a reference volume.
    :param element: The element to create the structure with.
    :return: The structure and the kpoint mesh (from fle, releted to the structure!).
    """
    import pymatgen as mg
#    import numpy as np
    kp=[0,0,0]  

    f=open('/home/bosonie/your/reference/file', 'r')
    for line in f:
        a=line.split()
        if a[0]==element:
	    kp[0]=int(a[1])
	    kp[1]=int(a[3])
	    kp[2]=int(a[5])
	    vol=a[7]
 
    in_structure = mg.Structure.from_file("/home/your/CIFsReproducibilityDFT/{0}.cif".format(element), primitive=False)
    newreduced=in_structure.copy()
    newreduced.scale_lattice(float(vol)*in_structure.num_sites)
    StructureData = DataFactory("structure")
    structure  = StructureData(pymatgen_structure=newreduced)
 
    # Create a structure data object
 #   StructureData = DataFactory("structure")
 #   structure = StructureData(cell=the_cell)
 #   structure.append_atom(position=(0., 0., 0.), symbols=str(element))
 #   structure.append_atom(position=(0.25*alat, 0.25*alat, 0.25*alat), symbols=str(element))
    return structure

@wf
def rescale(structure, scale):
    """
    Workfunction to rescale a structure

    :param structure: An AiiDA structure to rescale
    :param scale: The scale factor
    :return: The rescaled structure
    """
    the_ase = structure.get_ase()
    new_ase = the_ase.copy()
    new_ase.set_cell(the_ase.get_cell() * float(scale), scale_atoms=True)
    new_structure = DataFactory('structure')(ase=new_ase)
    return new_structure

@wf
def create_rescaled(element,scale):
    s0=structure_init(element)
    return rescale(s0,scale)

