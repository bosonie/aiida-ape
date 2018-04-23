#This code works just in this case and in this moment  in time when 
#I don't have any other calculation in the database.
#I will be more systematic with labels, description and extras in the future 
#in order to make the querying easier.

from aiida.orm.querybuilder import QueryBuilder
from aiida.orm.calculation.work import WorkCalculation
from common_wf import fit_birch_murnaghan_params, birch_murnaghan

q=QueryBuilder()
q.append(WorkCalculation, tag="wc", filters={'attributes._process_label':'EquationOfStatesHe'})
q.add_projection('wc', "id")

for i in q.iterall():
     p=load_node(i[0])
     if i[0]==507:
         print i[0]
     else:
         print i[0], p.inp.pseudo_path #, p.out.result.get_attr("eos_data")
         k=0
	 for i in p.out.initial_structure.sites:
	      k=k+1
	 vol=[]
         en=[]
         for s in range (5):
             # print float(p.out.result.get_attr("eos_data")[s][0]/k), float(p.out.result.get_attr("eos_data")[s][1]/k)
             vol.append(float(p.out.result.get_attr("eos_data")[s][0])/k)
             en.append(float(p.out.result.get_attr("eos_data")[s][1])/k)
         #print vol, en
         par, co = fit_birch_murnaghan_params(vol, en)
         print p.label, par

