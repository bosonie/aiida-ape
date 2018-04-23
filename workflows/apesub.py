
"""Submit a test calculation on localhost.

Usage: verdi run submit.py

Note: This script assumes you have set up computer and code as in README.md.
"""
import os
from aiida.orm.code import Code
from aiida.orm.computer import Computer
from aiida.orm import DataFactory
from aiida_ape.calculations.ape import ApeCalculation
from aiida.orm.data.parameter import ParameterData
from aiida_ape.data.elements import ELEMENTS
import sys
from aiida.orm.data.base import Str, Float

def generate_ApeCalculation(codename,element,s,p,d,f):
     
     inp = ApeCalculation.process().get_inputs_template()

     inp.code = Code.get_from_string(codename)
     inp._options.computer = Computer.get('localhost')
     inp._options.resources = {"num_machines": 1}

     check=False
     for ele in ELEMENTS:
     	if element == ele.symbol:
		nc=int(ele.number)
		check=True
     
     print check,nc
     if not check:
	 sys.exit("element is not valid")
     
     corpar=1
     if nc<=2:
	corpar=0
		
     parameters = ParameterData(dict={
                     'Title': '{}'.format(element),
                     'CalculationMode': 'ae + pp',
                     'Verbose': '40',
                     'WaveEquation': 'schrodinger',
                     'XCFunctional': 'lda_x + lda_c_pz',
                     'NuclearCharge': '{}'.format(nc),
                     'PPCalculationTolerance': '1.e-6',
                     'PPOutputFileFormat': 'upf + siesta',
                     'CoreCorrection': '{}'.format(corpar),
                     'EigenSolverTolerance': '1.e-8',
                     'ODEIntTolerance': '1.e-12'
                     })
     
    
     orbitals,PPComponents=get_orb_and_PPcomp(nc,s,p,d,f)

     inp.parameters = parameters
     inp.orbitals = orbitals
     inp.PPComponents = PPComponents

     inp._label = "{0} {1} {2} {3}".format(s,p,d,f)
     inp._description = "{} pseudo generation with cut of radii in label".format(element)


     return inp

def get_orb_and_PPcomp(nc,s,p,d,f):     
     if nc <= 2:
     	orbitals = ParameterData(dict={
           '%Orbitals': """
           1  |  0  | 1.000  | {0}
           2  |  1  | 0.000  | 0.000 
           3  |  2  | 0.000  | 0.000 
           4  |  3  | 0.000  | 0.000 
           % """.format(float(nc-1))
     	})
     
     	PPComponents = ParameterData(dict={
           '%PPComponents': """
           1  |  0  | {0}  | tm
           2  |  1  | {1}  | tm 
           3  |  2  | {2}  | tm 
           4  |  3  | {3}  | tm 
           % """.format(s,p,d,f),
     	})
     elif nc >=3 and nc <= 10:
     	orbitals = ParameterData(dict={
           '%Orbitals': """
           "He"
           2  |  0  | 1.000  | {0}
           2  |  1  | {1}    | {2}
           3  |  2  | 0.000  | 0.000 
           4  |  3  | 0.000  | 0.000 
           % """.format(float(int((nc-3)/(nc-3-0.00001))), lastp(nc), float(nc//8+(nc-1)//8+(nc-2)//8) )
     	})
     
     	PPComponents = ParameterData(dict={
          '%PPComponents': """
          2  |  0  | {0}  | tm
          2  |  1  | {1}  | tm 
          3  |  2  | {2}  | tm 
          4  |  3  | {3}  | tm 
          % """.format(s,p,d,f),
     	})
     elif nc >=11 and nc <= 18:
     	orbitals = ParameterData(dict={
          '%Orbitals': """
          "Ne"
          3  |  0  | 1.000  | {0}
          3  |  1  | {1}    | {2}
          3  |  2  | 0.000  | 0.000 
          4  |  3  | 0.000  | 0.000 
          % """.format(float(int((nc-11)/(nc-11-0.00001))), lastp(nc), float(nc//16+(nc-1)//16+(nc-2)//16) )
     	})
     
     	PPComponents = ParameterData(dict={
          '%PPComponents': """
          3  |  0  | {0}  | tm
          3  |  1  | {1}  | tm 
          3  |  2  | {2}  | tm 
          4  |  3  | {3}  | tm 
          % """.format(s,p,d,f),
     	})
     
     return orbitals, PPComponents     

     
def lastp(nc):
       if nc == 10 or nc == 18:
	  return 3.0
       else:
	  if nc >= 11:
		return float(nc//13+(nc-1)//13+(nc-2)//13)
	  else:
	  	return float(nc//5+(nc-1)//5+(nc-2)//5)
     
     
#     calc.store_all()
#     calc.submit()
#     print("submitted calculation; calc=Calculation(uuid='{}') # ID={}"\
#             .format(calc.uuid,calc.dbnode.pk))
