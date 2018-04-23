# -*- coding: utf-8 -*-
import json
from aiida.parsers.parser import Parser
from aiida_ape.calculations.ape import ApeCalculation
from aiida.parsers.exceptions import OutputParsingError
from aiida.orm.data.parameter import ParameterData

#from aiida.orm import CalculationFactory
#ApeCalculation = CalculationFactory('template.multiply')

#class ApeOutputParsingError(OutputParsingError):
#     pass
#---------------------------

class ApeParser(Parser):
    """
    Parser class for parsing output of multiplication.
    """

    def __init__(self, calculation):
#        """
#        Initialize Parser instance
#        """
        super(ApeParser, self).__init__(calculation)
#
#        # check for valid input
        if not isinstance(calculation, ApeCalculation):
            raise OutputParsingError("Can only parse ApeCalculation")

    # pylint: disable=protected-access
    def parse_with_retrieved(self, retrieved):
        """
        Parse output data folder, store results in database.

        :param retrieved: a dictionary of retrieved nodes, where
          the key is the link name
        :returns: a tuple with two values ``(bool, node_list)``, 
          where:

          * ``bool``: variable to tell if the parsing succeeded
          * ``node_list``: list of new nodes to be stored in the db
            (as a list of tuples ``(link_name, node)``)
        """
        success = False
        node_list=()

        #out_folder is the local folder where the retrived file are.
	#so one file to be parsed must be in the retrive_list 
        #specified in /calculation/ape.py

        try:
            out_folder = retrieved[self._calc._get_linkname_retrieved()]
        except KeyError:
	##    #raise IOError("No retrieved folder found")
            self.logger.error("No retrieved folder found")
            return success, node_list

        list_of_files = out_folder.get_folder_list()

        if self._calc._OUTPUT_FILE_NAME not in list_of_files:
            self.logger.error("Output file not found")
            return success, node_list

	with open( out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME) ) as f:
		for line in f:
			if "Wavefunction info:" in line:
				next(f)
				s=next(f).split()
				p=next(f).split()
				d=next(f).split()
				f=next(f).split()
	nodespicks={"s node": float(s[2]),
                    "s pick": float(s[3]),
		    "p node": float(p[2]),
                    "p pick": float(p[3]),
                    "d node": float(d[2]),
                    "d pick": float(d[3]),
                    "f node": float(f[2]),
		    "f pick": float(f[3])}

        if int(self._calc.inp.parameters.get_attr('CoreCorrection')) > 0:
        	with open( out_folder.get_abs_path(self._calc._OUTPUT_FILE_NAME) ) as f:
        	    for line in f:
		    	if "Core Corrections:" in line:
		    		l1=next(f).split()
		    		l2=next(f).split()

		cocor={"CoreCorrection scheme": l1[1],
        	   "CoreCorrection rc": float(l2[2])}
#		link_name = self.get_linkname_outparams()
#		nodes_list = [(link_name, s)]

	else:
		cocor={"CoreCorrection scheme": "no correction"}
#		link_name = self.get_linkname_outparams()
#		nodes_list = [(link_name, s)]
	
	parsed_dict = dict(nodespicks.items() + cocor.items())
	parr=ParameterData(dict=parsed_dict)
	link_name = self.get_linkname_outparams()
	nodes_list = [(link_name, parr)]

        from aiida_ape.data.elements import ELEMENTS
	nuclcharge=self._calc.inp.parameters.get_attr('NuclearCharge')
	Sy=ELEMENTS[int(nuclcharge)].symbol

        if "{}.ascii".format(Sy) not in list_of_files:
            self.logger.error("Siesta pseudo not found")
            return success, node_list

        if "{}.UPF".format(Sy) not in list_of_files:
            self.logger.error("UPF pseudo not found")
            return success, node_list

        from aiida_ape.data.psf import PsfData
        pseascii=PsfData()
        pseascii.set_file(out_folder.get_abs_path("{}.ascii".format(Sy)))
        nodes_list.append((self.get_linkname_pseascii(),pseascii))

	from aiida.orm.data.upf import UpfData
	pseupf=UpfData()
	pseupf.set_file(out_folder.get_abs_path("{}.UPF".format(Sy)))
        nodes_list.append((self.get_linkname_pseupf(),pseupf))

	success=True
        return success, nodes_list #out_nodes


    def get_linkname_pseupf(self):
        """                                                                     
        Returns the name of the link to the bands_array                        
        In Siesta, Node exists to hold the bands,
        pending the implementation of trajectory data.
        """
        return 'pseupf'


    def get_linkname_pseascii(self):
        """                                                                     
        Returns the name of the link to the bands_array                        
        In Siesta, Node exists to hold the bands,
        pending the implementation of trajectory data.
        """
        return 'pseascii'

