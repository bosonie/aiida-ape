import json

from aiida.orm.calculation.job import JobCalculation
from aiida.common.utils import classproperty
from aiida.common.exceptions import (InputValidationError, ValidationError)
from aiida.common.datastructures import (CalcInfo, CodeInfo)
from aiida.orm import DataFactory
from aiida.orm.data.parameter import ParameterData

#MultiplyParameters = DataFactory('template.factors')


class ApeCalculation(JobCalculation):
    """
    AiiDA calculation plugin for ape
    
    """

    def _init_internal_params(self):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(ApeCalculation, self)._init_internal_params()

        # Default Ape output parser provided by AiiDA
	# entry point defined in setup.json
        self._default_parser = "ape.parsers"


        self._INPUT_FILE_NAME = 'ape.in'
        self._OUTPUT_FILE_NAME = 'ape.out'
#        self._OUTPUT_PSEUDO_PSF = '*.ascii'
#	self._OUTPUT_PSEUDO_UPF = 'ape.UPF'

    @classproperty
    def _use_methods(cls):
        """
        Add use_* methods for calculations.
        
        Code below enables the usage
        my_calculation.use_parameters(my_parameters)
        """
        use_dict = JobCalculation._use_methods

	use_dict.update({
           "orbitals" : {
            'valid_types': ParameterData,
            'additional_parameter': None,
            'linkname': 'orbitals',
            'docstring': "Choose the input orbitals to use"
            }
	})

        use_dict.update({
           "PPComponents" : {
            'valid_types': ParameterData,
            'additional_parameter': None,
            'linkname': 'PPComponents',
            'docstring': "Choose the input PPComponents to generate"
            }
        })

        use_dict.update({
            "parameters": {
                'valid_types': ParameterData,
                'additional_parameter': None,
                'linkname': 'parameters',
                'docstring': "Use a node that specifies the input parameters "
            }
        })
        return use_dict

#    retdict["parameters"] = {


    def _prepare_for_submission(self, tempfolder, inputdict):
        """
        Create input files.

            :param tempfolder: aiida.common.folders.Folder subclass where
                the plugin should put all its files.
            :param inputdict: dictionary of the input nodes as they would
                be returned by get_inputs_dict
        """
        # Check inputdict
        try:
            parameters = inputdict.pop(self.get_linkname('parameters'))
        except KeyError:
            raise InputValidationError("No parameters specified for this calculation")
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters not of type ParameterData")

        try:
            code = inputdict.pop(self.get_linkname('code'))
        except KeyError:
            raise InputValidationError("No code specified for this "
                                       "calculation")

        try:
            PPComponents = inputdict.pop(self.get_linkname('PPComponents'))
        except KeyError:
            raise InputValidationError("No parameters specified for this calculation")
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters not of type ParameterData")

        try:
            orbitals = inputdict.pop(self.get_linkname('orbitals'))
        except KeyError:
            raise InputValidationError("No parameters specified for this calculation")
        if not isinstance(parameters, ParameterData):
            raise InputValidationError("parameters not of type ParameterData")


        if inputdict:
            raise ValidationError("Unknown inputs besides ParameterData")

    #    input_dict = parameters.get_dict()

        # Write input to file
        input_filename = tempfolder.get_abs_path(self._INPUT_FILE_NAME)
        input_params = parameters.get_dict()
        input_orbitals = orbitals.get_dict()
        input_PPComponents = PPComponents.get_dict()

	with open(input_filename, 'w') as infile:
        	for k, v in sorted(input_params.iteritems()):
                	infile.write(get_input_data_text(k, v))
         # json.dump(input_dict, infile)

        #        infile.write("#\n# -- Basis Set Info follows\n#\n")
                for k, v in input_orbitals.iteritems():
                	infile.write(get_input_data_text2(k, v))

        	for k, v in input_PPComponents.iteritems():
                	infile.write(get_input_data_text2(k, v))

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.retrieve_list = []
	calcinfo.retrieve_list.append(self._OUTPUT_FILE_NAME)
	calcinfo.retrieve_list.append('*.ascii')
        calcinfo.retrieve_list.append('*.UPF')

        codeinfo = CodeInfo()
        # will call ./code.py in.json out.json
        #cmdline_params = settings_dict.pop('CMDLINE', [])
        #codeinfo.cmdline_params = [
        #   < self._INPUT_FILE_NAME, ">", self._OUTPUT_FILE_NAME
        #]
        codeinfo.code_uuid = code.uuid
        codeinfo.stdin_name = self._INPUT_FILE_NAME
        codeinfo.stdout_name = self._OUTPUT_FILE_NAME
        calcinfo.codes_info = [codeinfo]

        return calcinfo

def get_input_data_text(key, val):
	return key + "=" + val + "\n"

def get_input_data_text2(key, val):
        return key + val + "\n"
