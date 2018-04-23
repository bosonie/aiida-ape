from aiida.backends.utils import load_dbenv, is_dbenv_loaded

if not is_dbenv_loaded():
    load_dbenv()

from aiida.orm import DataFactory
from aiida_quantumespresso.calculations.pw import PwCalculation
from aiida.orm.code import Code
import numpy as np
from aiida.orm.data.upf import UpfData


def generate_scf_input_params(structure, codename, pseudo, element):
    # The inputs
    inputs = PwCalculation.process().get_inputs_template()

    # The structure
    inputs.structure = structure

    inputs.code = Code.get_from_string(codename)
    # calc.label = "PW test"
    # calc.description = "My first AiiDA calculation of Silicon with Quantum ESPRESSO"
    inputs._options.resources = {"num_machines": 1}
    inputs._options.max_wallclock_seconds = 23*30*60
    queue="compute"
    if queue is not None:
    	inputs._options.queue_name=queue

    # Kpoints
    KpointsData = DataFactory("array.kpoints")
    kpoints = KpointsData()
#    kpoints_mesh = 2
    kp=[0,0,0]

    f=open('/home/bosonie/AIMS/LDARESULTS/NonRelBirchLDAref', 'r')
    for line in f:
        a=line.split()
        if a[0]==element:
            kp[0]=int(a[1])
            kp[1]=int(a[3])
            kp[2]=int(a[5])
            vol=a[7]

    kpoints.set_kpoints_mesh([1,1,1])#[kp[0], kp[1], kp[2]])
    inputs.kpoints = kpoints

    # Calculation parameters
    parameters_dict = {
        "CONTROL": {"calculation": "scf",
                    "tstress": True,  #  Important that this stays to get stress
                    "tprnfor": True,
                    "disk_io": "none"},
        "SYSTEM": {"ecutwfc": 100.,
                   "ecutrho": 200.,
		   "smearing": "gauss",
		   "degauss": 0.000734986},
        "ELECTRONS": {"conv_thr": 1.e-6}
    }
    ParameterData = DataFactory("parameter")
    inputs.parameters = ParameterData(dict=parameters_dict)

    pseudos = {}
    pseudos[element] = pseudo
    inputs.pseudo = pseudos
    
    return inputs


def birch_murnaghan(V, E0, V0, B0, B01):
    r = (V0 / V) ** (2. / 3.)
    return E0 + 9. / 16. * B0 * V0 * (r - 1.) ** 2 * \
                (2. + (B01 - 4.) * (r - 1.))


def fit_birch_murnaghan_params(volumes_, energies_):
    from scipy.optimize import curve_fit

    volumes = np.array(volumes_)
    energies = np.array(energies_)
    params, covariance = curve_fit(
        birch_murnaghan, xdata=volumes, ydata=energies,
        p0=(
            energies.min(),  # E0
            volumes.mean(),  # V0
            0.1,  # B0
            3.,  # B01
        ),
        sigma=None
    )
    return params, covariance


def diff_murn_squared(V, Vo, Bo, Bp, Vo2, Bo2, Bp2):
    return (birch_murnaghan(V, 0, Vo, Bo, Bp)-birch_murnaghan(V, 0, Vo2, Bo2, Bp2))**2


def get_reference(element):
    f=open('AIMS/LDARESULTS/NonRelBirchLDAref', 'r')
    for line in f:
    	a=line.split()
    	if a[0]==element:
            Vo2=float(a[7])
            Bp2=float(a[9])
            Bo2=float(a[8])/160.21766208  #conversion from GPa to eV/Ang^3
            print "Reference", Vo2, Bo2, Bp2
    	    return Vo2, Bo2, Bp2

def plot_eos(eos_pk):
    """
    Plots equation of state taking as input the pk of the ProcessCalculation 
    printed at the beginning of the execution of run_eos_wf 
    """
    import pylab as pl
    from aiida.orm import load_node
    eos_calc=load_node(eos_pk)
    eos_result=eos_calc.out.result
    raw_data = eos_result.dict.eos_data
    
    data = []
    for V, E, units in raw_data:
        data.append((V,E))
      
    data = np.array(data)
    params, covariance = fit_birch_murnaghan_params(data[:,0],data[:,1])
    
    vmin = data[:,0].min()
    vmax = data[:,0].max()
    vrange = np.linspace(vmin, vmax, 300)

    pl.plot(data[:,0],data[:,1],'o')
    pl.plot(vrange, birch_murnaghan(vrange, *params))

    pl.xlabel("Volume (ang^3)")
    # I take the last value in the list of units assuming units do not change
    pl.ylabel("Energy ({})".format(units))
    pl.show()

