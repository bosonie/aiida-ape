AiiDA Ape plugin and workflows
==============================

AiiDA plugin for ape 2.2.0 (http://www.tddft.org/programs/APE),
a pseudopotential engine able to create pseudopotential for SIESTA, PWscf, ABINIT, OCTOPUS.

Extremely basic version, built for personal needs.
The inputs are simple ParameterData end essentially only the generated SIESTA
and PWscf pseudopotential are retrieved and stored in the database.
ABINIT, OCTOPUS pseudopotential are not supported yet!
Not even the error menagement is properly coded.
Documentetion not provoded yet.

A complete example of how to submit a test calculation using this plugin
is in the folder examples.

Installation and setup
======================

* Install aiida core (http://www.aiida.net/) and follow the setup
* mkdir aiida-ape
* cd aiida-ape
* git clone https://github.com/bosonie/aiida-ape
* pip install -e .
* reentry scan -r aiida

As the ape code is serial and the pseudo generation is not demanding, it is always suggested to to have it in your local machine.
This means you have to 
* add local machine to the list of computers:
   verdi computer setup
   At any prompt, type ? to get some help.
   ---------------------------------------
   => Computer name: localhost
   Creating new computer with name 'localhost'
   => Fully-qualified hostname: localhost
   => Description: my local computer
   => Enabled: True
   => Transport type: local
   => Scheduler type: direct
   => AiiDA work directory: /tmp
   => mpirun command:
   => Default number of CPUs per machine: 4
   => Text to prepend to each command execution:
      # This is a multiline input, press CTRL+D on a
      # empty line when you finish
      # ------------------------------------------
      # End of old input. You can keep adding
      # lines, or press CTRL+D to store this value
      # ------------------------------------------
   => Text to append to each command execution:
      # This is a multiline input, press CTRL+D on a
      # empty line when you finish
      # ------------------------------------------
      # End of old input. You can keep adding
      # lines, or press CTRL+D to store this value
      # ------------------------------------------
   Computer 'localhost' successfully stored in DB.
   pk: 1, uuid: a5b452f0-ec1e-4ec2-956a-10a416f60ed3
   Note: before using it with AiiDA, configure it using the command
     verdi computer configure localhost
   (Note: machine_dependent transport parameters cannot be set via
   the command-line interface at the moment)

   verdi computer configure localhost 
   Configuring computer 'localhost' for the AiiDA user 'user@tcd.ie'
   Computer localhost has transport of type local
   There are no special keys to be configured. Configuration completed.
Code setup is the same as every other code, be carefull at the line
"Folder with the code". You put there the folder where your code is.
All the files in that directory will be copied in the running directory.
Line "Relative path of the executable" specifies the name of the executable
to be run, the executable could be in a subfolder of the folder
specified in "Folder with the code".
   $ verdi code setup  # set up (local) code
   At any prompt, type ? to get some help.
   ---------------------------------------
   => Label: aiida_ape
   => Description: aiida template plugin
   => Local: True
   => Default input plugin: ape.ape
   => Folder with the code: /your/path/to/ape/executable
   => Relative path of the executable: ape
   => Text to prepend to each command execution
   FOR INSTANCE, MODULES TO BE LOADED FOR THIS CODE:
      # This is a multiline input, press CTRL+D on a
      # empty line when you finish
      # ------------------------------------------
      # End of old input. You can keep adding
      # lines, or press CTRL+D to store this value
      # ------------------------------------------
   => Text to append to each command execution:
      # This is a multiline input, press CTRL+D on a
      # empty line when you finish
      # ------------------------------------------
      # End of old input. You can keep adding
      # lines, or press CTRL+D to store this value
      # ------------------------------------------
   Code 'aiida_ape' successfully stored in DB.
   pk: 1, uuid: 7627c747-b7f2-4717-b0fa-94e53915e422


Workflow
========

I built the plugin just because I wanted to use it within a workflow to test 
.UPF pseudopotential. The workflow I wrote is in the folder /workflows.
To use the workflow you need aiida-quantumespresso and the related setup.
The workflow at the moment works only if you copy it in you virtualenvironment/bin folder
or in your PYTHON PATH if you don't use virtual environment.
Waiting updates on the new workflow system from aiidateam before stabilizing the workflow
