from create_rescale import structure_init, rescale
from common_wf import generate_scf_input_params, fit_birch_murnaghan_params
from aiida.work.workchain import WorkChain, ToContext, Outputs
from aiida.orm.calculation.work import WorkCalculation
from aiida.work.run import run, submit
from aiida.orm.data.base import Str, Float
from aiida_quantumespresso.calculations.pw import PwCalculation
from aiida.work.process_registry import ProcessRegistry
from aiida.orm.data.structure import StructureData
from aiida.orm.data.parameter import  ParameterData
from aiida.orm.data.upf import UpfData
from aiida.orm import load_node
#from aiida import load_dbenv
#from aiida import is_dbenv_loaded
#if not is_dbenv_loaded():
#    load_dbenv()


    
scale_facs = (0.94, 0.96, 0.98, 1.0, 1.02, 1.04, 1.06)
labels = ["c1", "c2", "c3", "c4", "c5","c6", "c7"]

class EquationOfStates(WorkChain):
    @classmethod
    def define(cls, spec):
        super(EquationOfStates, cls).define(spec)
        spec.input("element", valid_type=Str)
        spec.input("code", valid_type=Str)
        spec.input("pseudo", valid_type=UpfData)
        spec.outline(
            cls.run_pw,
            cls.return_results,
        )
	spec.output('initial_structure', valid_type=StructureData)
	spec.output('result', valid_type=ParameterData)
	spec.output('fit_res', valid_type=ParameterData)
        #spec.dynamic_output()

    def run_pw(self):
        print "Workchain node identifiers: {}".format(ProcessRegistry().current_calc_node)
        #Instantiate a JobCalc process and create basic structure
        JobCalc = PwCalculation.process()
        self.ctx.s0 = structure_init(Str(self.inputs.element))
        self.ctx.eos_names = []

        calcs = {}
        for label, factor in zip(labels, scale_facs):
            s = rescale(self.ctx.s0,Float(factor))
            inputs = generate_scf_input_params(s, str(self.inputs.code), self.inputs.pseudo, str(self.inputs.element))
            print "Running a scf for {} with scale factor {}".format(self.inputs.element, factor)
            future = submit(JobCalc, **inputs)
            calcs[label] = Outputs(future)
          
        # Ask the workflow to continue when the results are ready and store them
        # in the context
        return ToContext(**calcs)  #Here it waits

    def return_results(self):
        eos = []
        for label in labels:
            eos.append(get_info(self.ctx[label]))
	k=0
	for i in self.ctx.s0.sites:
		k=k+1
	vol=[]
        en=[]
        for s in range (7):
            vol.append(float(eos[s][0])/k)
            en.append(float(eos[s][1])/k)
	par, co = fit_birch_murnaghan_params(vol, en)
        #Return information to plot the EOS
#        ParameterData = DataFactory("parameter")
        #retdict = {
        self.out('initial_structure', self.ctx.s0)#,
        self.out('result', ParameterData(dict={'eos_data': eos}))#,
	self.out('fit_res', ParameterData(dict={ 'E0': par[0],
						'E0 units' : "eV/atm",
						'V0': par[1],
						'V0 units' : "ang^3/atm",
					        'B0': par[2],
						'B0 units' : "eV/Ang^3",
					        'B1': par[3]}))
                #)
        #for link_name, node in retdict.iteritems():
        #    self.out(link_name, node)

def get_info(calc_results):
    return (calc_results['output_parameters'].dict.volume,
            calc_results['output_parameters'].dict.energy,
            calc_results['output_parameters'].dict.energy_units)

