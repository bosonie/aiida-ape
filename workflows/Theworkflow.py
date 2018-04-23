from aiida.work.workchain import WorkChain, ToContext, Outputs, while_
from aiida.work.run import run, submit
from aiida.orm.data.base import Str, Float
from aiida.work.process_registry import ProcessRegistry
from aiida.orm import DataFactory
from aiida.orm.data.upf import UpfData
from equation_of_states import EquationOfStates
from apesub import generate_ApeCalculation
from aiida_ape.calculations.ape import ApeCalculation
from scipy.integrate import quad
from common_wf import diff_murn_squared, get_reference
from numpy import sqrt

class TheWorkflow(WorkChain):
    @classmethod
    def define(cls, spec):
        super(TheWorkflow, cls).define(spec)
        spec.input("element", valid_type=Str)
        spec.outline(
            cls.init,
	    cls.set_flow,
            while_(cls.not_finished)(
                cls.run_ape,
                cls.runEos,
		cls.res_on_variable,
            ),
            cls.return_res
        )
        spec.dynamic_output()


    def init(self):
	print "Workchain node identifiers: {}".format(ProcessRegistry().current_calc_node)
	print "Run Ape with guess radii, just to get nodes and picks"
	apein=generate_ApeCalculation('apelocal',self.inputs.element,2,2,2,2)
	self.ctx.Vo2, self.ctx.Bo2, self.ctx.Bp2 = get_reference(self.inputs.element)
	future = submit(ApeCalculation.process(), **apein)
	return ToContext(result=future)

    def set_flow(self):
	self.ctx.spick=self.ctx.result.out.output_parameters.get_attr('s pick')
	self.ctx.snode=self.ctx.result.out.output_parameters.get_attr('s node')
        self.ctx.ppick=self.ctx.result.out.output_parameters.get_attr('p pick')
        self.ctx.pnode=self.ctx.result.out.output_parameters.get_attr('p node')
	print self.ctx.spick, self.ctx.ppick
	self.ctx.scales = (1., 1.2)
	self.ctx.si = 0
	self.ctx.pi = 0
	self.ctx.fin = []

    def not_finished(self):
	return self.ctx.pi < len(self.ctx.scales)

    def run_ape(self):
	self.ctx.scut=self.ctx.scales[self.ctx.si]*self.ctx.spick
	self.ctx.pcut=self.ctx.scales[self.ctx.pi]*self.ctx.ppick
	self.ctx.dcut=self.ctx.scut
	self.ctx.fcut=self.ctx.scut
	print "Run Ape with s cutoff = {0} and p cutoff = {1}".format(self.ctx.scut,self.ctx.pcut)
	inp=generate_ApeCalculation('apelocal',self.inputs.element,self.ctx.scut,self.ctx.pcut,self.ctx.dcut,self.ctx.fcut)
        futur = submit(ApeCalculation.process(), **inp)
        return ToContext(resul=futur)

    def runEos(self):
	inputs = dict = {'element' : self.inputs.element}
	inputs['code']=Str('QEmodule@parsons')
        pseu=self.ctx.resul.out.pseupf
	inputs['pseudo']=pseu
	inputs['_label']="{0} {1} {2} {3}".format(self.ctx.scut,self.ctx.pcut,self.ctx.dcut,self.ctx.fcut)
	inputs['_description']="T1"
	print "Runnin eos"
	fut = submit(EquationOfStates, **inputs)
        return ToContext(res=fut)  #Here it waits

    def res_on_variable(self):
	self.ctx.si += 1
	if self.ctx.si == len(self.ctx.scales):
		self.ctx.si = 0
		self.ctx.pi += 1
	Vo=self.ctx.res.out.fit_res.get_attr('V0')
	Bo=self.ctx.res.out.fit_res.get_attr('B0')
	Bp=self.ctx.res.out.fit_res.get_attr('B1')
	Vm=(Vo+self.ctx.Vo2)/2
	I = quad(diff_murn_squared, 0.94*Vm, 1.06*Vm , args=(Vo, Bo, Bp, self.ctx.Vo2, self.ctx.Bo2, self.ctx.Bp2))
	self.ctx.fin.append((self.ctx.res.label,Vo,Bo*160.21766208,Bp,sqrt(I[0]/Vm/0.12)*1000, "meV"))

    def return_res(self):
        ParameterData = DataFactory("parameter")
	ref=[(self.ctx.Vo2, self.ctx.Bo2*160.21766208, self.ctx.Bp2, self.ctx.Bo2)]
        retdict = {
                'result': ParameterData(dict={'deltares': self.ctx.fin,
						'reference' : ref})
           }
        for link_name, node in retdict.iteritems():
            self.out(link_name, node)


element="C"
run(TheWorkflow, element=Str(element), _label="T")
