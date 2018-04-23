# -*- coding: utf-8 -*-
"""Submit a test calculation on localhost.

Usage: verdi run submit.py

Note: This script assumes you have set up computer and code as in README.md.
"""
import os
from aiida.orm import DataFactory

ParameterData = DataFactory('parameter')

parameters = ParameterData(dict={
                'Title': 'C',
                'CalculationMode': 'ae + pp',
                'Verbose': '40',
                'WaveEquation': 'schrodinger',
                'XCFunctional': 'lda_x + lda_c_pz',
                'NuclearCharge': '6',
                'PPCalculationTolerance': '1.e-6',
                'PPOutputFileFormat': 'upf + siesta',
                'CoreCorrection': '1',
                'EigenSolverTolerance': '1.e-8',
                'ODEIntTolerance': '1.e-12'
                })


orbitals = ParameterData(dict={
'%Orbitals': """
"He"
  2  |  0  | 1.000  | 1.000
  2  |  1  | 1.000  | 1.000 
  3  |  2  | 0.000  | 0.000 
  4  |  3  | 0.000  | 0.000 
  % """
})

PPComponents = ParameterData(dict={
'%PPComponents': """
  2  |  0  | 1.300  | tm
  2  |  1  | 1.300  | tm 
  3  |  2  | 1.500  | tm 
  4  |  3  | 1.500  | tm 
  % """,
})




# use code name specified using 'verdi code setup'
code = Code.get_from_string('apelocal')

# use computer name specified using 'verdi computer setup'
computer = Computer.get('localhost')




# Prepare input parameters
#MultiplyParameters = DataFactory('template.factors')
#parameters = MultiplyParameters(x1=2, x2=3)

# set up calculation
calc = code.new_calc()
calc.label = "aiida_ape test 0"
calc.description = "Test job submission with the aiida_ape plugin"
#calc.set_max_wallclock_seconds(30 * 60)  # 30 min
# This line is only needed for local codes, otherwise the computer is
# automatically set from the code
calc.set_computer(computer)
calc.set_withmpi(False)
calc.set_resources({"num_machines": 1})
calc.use_parameters(parameters)
calc.use_orbitals(orbitals)
calc.use_PPComponents(PPComponents)

#subfolder, script_filename = calc.submit_test()
#path = os.path.relpath(subfolder.abspath)
#print("submission test successful")#
#print("Find remote folder in {}".format(path))
#print("In order to actually submit, add '--submit'")



calc.store_all()
calc.submit()
print("submitted calculation; calc=Calculation(uuid='{}') # ID={}"\
        .format(calc.uuid,calc.dbnode.pk))
