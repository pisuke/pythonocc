# -*- coding: iso-8859-1 -*-
#! /usr/bin/python

##Copyright 2008-2009 Thomas Paviot (thomas.paviot@free.fr)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##
##You should have received a copy of the GNU General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import os, os.path
import sys
sys.path.append("../..")
import glob
import datetime
try:
    from pygccxml import declarations
    from pyplusplus import module_builder
    from pyplusplus.module_creator import sort_algorithms
    from pyplusplus.module_builder import call_policies
    HAVE_PYGCCXML = True
except ImportError:
    HAVE_PYGCCXML = False

import environment
import BuildDocstring

def CaseSensitiveGlob(wildcard):
    """
    Case sensitive glob for Windows.
    Designed for handling of GEOM and Geom modules
    This function makes the difference between GEOM_* and Geom_* under Windows
    """
    flist = glob.glob(wildcard)
    pattern = wildcard.split('*')[0]
    f = []
    for file in flist:
        if pattern in file:
            f.append(file)
    return f

def WriteDisclaimerHeader(fp):
    header = """/*
READ CAREFULLY the OpenCascade and CeCILL-A licenses before redistributing this package.
*/
"""
    fp.write(header)

def WriteLicenseHeader(fp):
    header = """/*

Copyright 2008-2009 Thomas Paviot (thomas.paviot@free.fr)

This file is part of pythonOCC.

pythonOCC is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pythonOCC is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

*/
"""
    fp.write(header)
    
PYOCC_HEADER_TEMPLATE = """

%include typemaps.i
%include cmalloc.i
%include cpointer.i
%include carrays.i
%include exception.i
%include std_list.i
%include std_string.i

#ifndef _Standard_TypeDef_HeaderFile
#define _Standard_TypeDef_HeaderFile
#define Standard_False (Standard_Boolean) 0
#define Standard_True  (Standard_Boolean) 1
#endif

/*
Exception handling
*/
%{#include <Standard_Failure.hxx>%}
%exception
{
    try
    {
        $action
    } 
    catch(Standard_Failure)
    {
        SWIG_exception(SWIG_RuntimeError,Standard_Failure::Caught()->DynamicType()->Name());
    }
}

/*
Standard_Real & function transformation
*/
%typemap(argout) Standard_Real &OutValue {
    PyObject *o, *o2, *o3;
    o = PyFloat_FromDouble(*$1);
    if ((!$result) || ($result == Py_None)) {
        $result = o;
    } else {
        if (!PyTuple_Check($result)) {
            PyObject *o2 = $result;
            $result = PyTuple_New(1);
            PyTuple_SetItem($result,0,o2);
        }
        o3 = PyTuple_New(1);
        PyTuple_SetItem(o3,0,o);
        o2 = $result;
        $result = PySequence_Concat(o2,o3);
        Py_DECREF(o2);
        Py_DECREF(o3);
    }
}

%typemap(in,numinputs=0) Standard_Real &OutValue(Standard_Real temp) {
    $1 = &temp;
}

/*
Standard_Integer & function transformation
*/
%typemap(argout) Standard_Integer &OutValue {
    PyObject *o, *o2, *o3;
    o = PyInt_FromLong(*$1);
    if ((!$result) || ($result == Py_None)) {
        $result = o;
    } else {
        if (!PyTuple_Check($result)) {
            PyObject *o2 = $result;
            $result = PyTuple_New(1);
            PyTuple_SetItem($result,0,o2);
        }
        o3 = PyTuple_New(1);
        PyTuple_SetItem(o3,0,o);
        o2 = $result;
        $result = PySequence_Concat(o2,o3);
        Py_DECREF(o2);
        Py_DECREF(o3);
    }
}

%typemap(in,numinputs=0) Standard_Integer &OutValue(Standard_Integer temp) {
    $1 = &temp;
}

"""

nb_exported_classes = 0

class ModularBuilder(object):
    """
    This class generates a set of .i files integrated in one OCC.i script. The result is
    a simple _OCC.pyd and OCC.py script that enable better handliing of different OCC classes.
    """
    def __init__( self , module, generate_doc = False, INC_PATH = environment.OCC_INC):
        self.MODULES = module
        self.MODULE_NAME = module[0]
        self.INC_PATH = INC_PATH #the path where are the headers to parse can be OCC_INC or SALOME_GEOM_INC
        self._generate_doc = generate_doc
        if self._generate_doc:
            self.WriteLicenseHeader = WriteDisclaimerHeader
        else:
            self.WriteLicenseHeader = WriteLicenseHeader
        self._mb = None
        self.fp = None
        self.occ_fp = None
        self.dependencies_fp = None
        self.module_dependencies = []
        self.dependencies_headers_to_write = []
        self._available_occ_packages = []
        # The name of the header file to be parsed by gccxml/pygccxml
        self._wrapper_filename = os.path.join(os.getcwd(),'%s'%environment.SWIG_FILES_PATH_MODULAR,'%s_Wrapper.hxx'%self.MODULE_NAME)
        # A dict contains all parent classes of a given class
        self.DERIVED = {}
        # Two lists containing typedefs and enums
        self._typedef_list = []
        self._enum_list = []
        # A list containing all necessary headers to achieve compilation        
        self.ADDITIONAL_HEADERS = module[1]
        self.ADDITIONAL_HXX = []
        self.NEEDED_HXX = []
        self.IMPORTED_MODULES = []
        self.MEMBER_FUNCTIONS_TO_EXCLUDE = {}
        self.ClassDocstring = ""
        self.MemberfunctionDocStrings = {}
        self.ALREADY_EXPOSED = []
        self.CLASSES_TO_EXCLUDE = []
        self.InitBaseSwigFile()
        self.FindClasseToExclude()
        self.FindMemberFunctionsToExclude()     
        self.Init()     
        self.GenerateSWIGSourceFile()
        self.WriteDepencyFile()
        self.WriteHeaderFile()
        
    def BuildClassHierarchy(self):
        """
        Directory of class hierarchy
        Ex: DERIVED = {"104":[Voiture],"106":[Voiture]}
        """
        all_classes = self._mb.classes()
        classes_declarations = all_classes.declarations
        for class_declaration in classes_declarations:
            class_name = class_declaration.name
            derived = class_declaration.derived
            if len(derived)>0:
                for der in derived:
                    self.DERIVED[der.related_class.name]=class_name
       
    def BuildTypedefList(self):
        """
        Fill in the typedef_list with all typedef defined in this module
        """
        typedefs = self._mb.global_ns.typedefs()
        for typedef in typedefs:
            typedef_name = typedef.name
            self._typedef_list.append(typedef_name)
    
    def BuildEnumList(self):
        """
        Fill in the enum_list with all enums defined in this module
        """
        try:#eeror with BRepBndLib on Linux
            for enum in self._mb.enumerations():
                enum_name = enum.name
                self._enum_list.append(enum_name)
        except:
            pass
        
    def GenerateSWIGSourceFile(self):
        """
        .i file creation
        """
        self.GenerateWrapper()
        self.BuildModule()
        self.BuildTypedefList()
        self.BuildEnumList()
        self.BuildClassHierarchy()
        # File creation
        self.fp = self.occ_fp
        self.WriteModuleTypedefs()
        self.WriteModuleEnums()
        # Classes processing (if any class defined in the module)
        try:
            handle_classes_to_expose = self._mb.classes(lambda decl: (decl.name.lower().startswith(("Handle_%s_"%self.MODULE_NAME).lower())))
            for class_declaration in handle_classes_to_expose:
                if not class_declaration.name in self.CLASSES_TO_EXCLUDE:
                    self.process_class(class_declaration)
        except RuntimeError:
            print "No handles defined."
        try:
            classes_to_expose = self._mb.classes(lambda decl: (decl.name.lower().startswith(("%s_"%self.MODULE_NAME).lower())) or decl.name==self.MODULE_NAME)
            for class_declaration in classes_to_expose:
                if not class_declaration.name in self.CLASSES_TO_EXCLUDE:
                    self.process_class(class_declaration)
        except RuntimeError:
            print "No class defined."
        self.fp.close()

    def AddDependency(self, module_name):
        """
        Add a dependency with other module.
        """
        if module_name=='GEOM':
            module_name='SGEOM'
        if 'XW' in module_name: #TODO: better handling of XW.i dependency with Xw module under Linux
            return True
        if module_name == 'Selector': #SalomeGEOM
            return True
        if sys.platform=='win32' and module_name=='WNT':
            return True
        if sys.platform=='win32' and module_name=='Xw':
            return True
        if not module_name in self.module_dependencies:
            self.module_dependencies.append(module_name)
            if module_name=='TCollection':
                self.dependencies_headers_to_write += CaseSensitiveGlob(os.path.join(self.INC_PATH,'Handle_%s_*.hxx'%module_name))
                if self.INC_PATH == environment.SALOME_GEOM_INC:
                    self.dependencies_headers_to_write += CaseSensitiveGlob(os.path.join(environment.OCC_INC,'Handle_%s_*.hxx'%module_name))
            else:
                self.dependencies_headers_to_write += CaseSensitiveGlob(os.path.join(self.INC_PATH,'%s_*.hxx'%module_name))+\
                CaseSensitiveGlob(os.path.join(self.INC_PATH,'Handle_%s_*.hxx'%module_name))
                if self.INC_PATH == environment.SALOME_GEOM_INC:
                    self.dependencies_headers_to_write += CaseSensitiveGlob(os.path.join(environment.OCC_INC,'%s_*.hxx'%module_name))+\
                CaseSensitiveGlob(os.path.join(environment.OCC_INC,'Handle_%s_*.hxx'%module_name))                    
            self.dependencies_headers_to_write = self.OSFilterHeaders(self.dependencies_headers_to_write)
    
    def WriteDepencyFile(self):
        """
        Generate the file for dependencies.
        """
        if self.MODULE_NAME=='GEOM':
            self.MODULE_NAME='SGEOM'#back to the good name
        dependencies_fp = open(os.path.join(os.getcwd(),'%s'%environment.SWIG_FILES_PATH_MODULAR,'%s_dependencies.i'%self.MODULE_NAME),"w")
        WriteLicenseHeader(dependencies_fp)
        self.dependencies_headers_to_write.sort()
        if len(self.module_dependencies)==0:
            return True
        dependencies_fp.write("%{\n")
        for header_to_write in self.dependencies_headers_to_write:
            dependencies_fp.write("#include <%s>\n"%os.path.basename(header_to_write))
        dependencies_fp.write("%};\n\n")
        # Adding imports
        for module_name in self.module_dependencies:
            dependencies_fp.write("%%import %s.i\n"%module_name)
        dependencies_fp.close()
    
    def WriteHeaderFile(self): 
        """
        Write the SWIG file that contains all required headers for compilation.
        """
        print self.MODULE_NAME
        if self.MODULE_NAME=='GEOM':
            self.MODULE_NAME='SGEOM'#back to the good name
        already_written = []
        headers_fp = open(os.path.join(os.getcwd(),'%s'%environment.SWIG_FILES_PATH_MODULAR,'%s_headers.i'%self.MODULE_NAME),"w")
        WriteLicenseHeader(headers_fp)
         # Write includes
        headers_fp.write("%{\n")
        headers_fp.write("\n// Headers necessary to define wrapped classes.\n\n")
        for hxx_file in self.HXX_FILES:
            if not hxx_file in already_written:
                headers_fp.write("#include<%s>\n"%os.path.basename(hxx_file))
                already_written.append(hxx_file)
        headers_fp.write("\n// Additional headers necessary for compilation.\n\n")
        self.ADDITIONAL_HXX = self.OSFilterHeaders(self.ADDITIONAL_HXX)
        for hxx_file in self.ADDITIONAL_HXX:
            if not hxx_file in already_written:
                headers_fp.write("#include<%s>\n"%os.path.basename(hxx_file))
                already_written.append(hxx_file)
        # NEEDED_HXX:
        headers_fp.write("\n// Needed headers necessary for compilation.\n\n")
        self.NEEDED_HXX = self.OSFilterHeaders(self.NEEDED_HXX)
        for hxx_file in self.NEEDED_HXX:
            if os.path.isfile(os.path.join(self.INC_PATH,hxx_file)):
                if not hxx_file in already_written:
                    headers_fp.write("#include<%s>\n"%os.path.basename(hxx_file))
                    already_written.append(hxx_file)
        headers_fp.write("%}\n")
        headers_fp.close()

    def CheckDepedency(self,return_type):
        #
        # Check what headers to add for the return type
        #
        t = self.CheckParameterIsTypedef(return_type)
        if t:
            if (t!=self.MODULE_NAME):# and (t!='Standard'):
                if t.startswith('Handle'):
                    t = t.split('_')[1]
                self.AddDependency(t)#print "Dependency with module %s"%t
        else:#it's not a type def
            if (not return_type.startswith('%s_'%self.MODULE_NAME)) and \
            (not return_type.startswith('Handle_%s_'%self.MODULE_NAME)) and \
            (not return_type in ['void','int']) and (not '::' in return_type):#external dependency. Add header
                header_to_add = '%s.hxx'%return_type
                if not (header_to_add in self.NEEDED_HXX):
                    self.NEEDED_HXX.append('%s.hxx'%return_type)
    
    def write_function( self , mem_fun , parent_is_abstract):
        """
        Write member functions declarations
        """
        # Test if method already exposed
        is_exportable = mem_fun.exportable
        function_name = mem_fun.name
        class_parent_name = mem_fun.parent.name
        if (not is_exportable) and not(class_parent_name in function_name):#for constructors and destructor
            print "\t\t %s method not exportable"%function_name
            return True
        if ("operator=" in function_name and not "==" in function_name):#not wrapped by SWIG
            return True
        if ("operator ::" in function_name): #Pb with SWIG
            return True
        if hasattr(mem_fun,"return_type"):
            return_type = "%s"%mem_fun.return_type
        else:
            print "NOTHING!!!"
            return False
        #
        # Check what headers to add for the return type
        #
        if return_type!='None' and not (' ' in return_type):
            t = self.CheckParameterIsTypedef(return_type)
            if t:
                if (t!=self.MODULE_NAME):# and (t!='Standard'):
                    if t.startswith('Handle'):
                        t = t.split('_')[1]
                    self.AddDependency(t)#print "Dependency with module %s"%t
            else:#it's not a type def
                if (not return_type.startswith('%s_'%self.MODULE_NAME)) and \
                (not return_type.startswith('Handle_%s_'%self.MODULE_NAME)) and \
                (not return_type in ['void','int']) and (not '::' in return_type):#external dependency. Add header
                    header_to_add = '%s.hxx'%return_type
                    if not (header_to_add in self.NEEDED_HXX):
                        self.NEEDED_HXX.append('%s.hxx'%return_type)
        #print return_type
        print "\t\t %s added."%function_name
        # FEATURE AUTODOC
        to_write = '\t\t%feature("autodoc", "1");\n'
        # FEATURE DOCSTRING
        # First try to find the key (necessary for overloaded functions
        # the key can be Coord, Coord_1 or Coord_2
        if self.MemberfunctionDocStrings.has_key(function_name):
            key = function_name
        if self._generate_doc and not ('Handle' in class_parent_name) and key!=None:#self.MemberfunctionDocStrings.has_key(function_name):
            docstring = self.MemberfunctionDocStrings.pop(key)#
            to_write += '\t\t%feature("docstring") '
            to_write += '%s '%function_name
            try:
                to_write += '"""%s""";\n'%docstring
            except UnicodeDecodeError:
                to_write += '"UnicodeDecodeError while parsing docstring;"\n'
                print "UnicodeDecodeError"
        # Detect virtuality
        if (mem_fun.virtuality==declarations.VIRTUALITY_TYPES.PURE_VIRTUAL) or (mem_fun.virtuality==declarations.VIRTUALITY_TYPES.VIRTUAL):
            to_write+="\t\tvirtual"
        # on teste le cas suivant pour return_type:gp_Pnt const &, qu'il faut transformer en const gp_Pnt &
        parts = return_type.split(" ")
        if len(parts)==3:
            return_type="%s %s %s"%(parts[1],parts[0],parts[2])
        if return_type=="None":
            to_write += "\t\t%s("%(function_name)
        else:
            to_write +="\t\t%s %s("%(return_type,function_name)
        arguments = mem_fun.arguments

        is_first = True
        for i in range(len(arguments)):
            argument = arguments[i]
            if i<len(arguments)-1:
                next_argument = arguments[i+1]
                next_argument_default_value = "%s"%next_argument.default_value
            else:
                next_argument_default_value = "PP"
            if not is_first:
                to_write += ", "
            argument_name = "%s"%argument.name
            argument_type = "%s"%argument.type
            argument_types=argument_type.split(" ")
            #
            # Check if the parameter is a typedef defined in another OCC package
            #
            argument_type_name = argument_types[0]
            #
            # The argument type_name may be Standard_Real, gp_Pnt etc.
            # The associated header must be added to the swig .if file in order to 
            # properly compile. This is then the strategy:
            # Example: V3d package is parsed
            #    - if the argument_type_name startswith V3d_, it's defined in this module. Pass.
            #    - if the argument_type_name does'nt start with V3d, (for ex gp_), then add the header
            #    to the list of additionnal headers.
            # 
            #
            t = self.CheckParameterIsTypedef(argument_type_name)
            if t:
                if (t!=self.MODULE_NAME):# and (t!='Standard'):
                    self.AddDependency(t)#print "Dependency with module %s"%t
            else:#it's not a type def
                if (not argument_type_name.startswith('%s_'%self.MODULE_NAME)) and \
                (not argument_type_name.startswith('Handle_%s_'%self.MODULE_NAME)) and\
                (not '::' in argument_type_name) and \
                (not argument_type in ['int']):#external dependency. Add header
                    header_to_add = '%s.hxx'%argument_type_name
                    if not (header_to_add in self.NEEDED_HXX):
                        self.NEEDED_HXX.append('%s.hxx'%argument_type_name)
            #
            # Find argument default value
            #
            argument_default_value = "%s"%argument.default_value
            #print argument_types, len(argument_types)
            #print argument_default_value
#            if argument_types[0]=='GEOM_Engine':
#                print argument_types, argument_name
#                sys.exit(0)
            if len(argument_types)==1:
                to_write += "%s "%argument_types[0]
            elif argument_types[0].startswith('std::list'):
                #We have something like:
                #['std::list<Handle_GEOM_Object,std::allocator<Handle_GEOM_Object>', '>'] 2
                #
                tmp = argument_types[0]
                tmp = tmp.split('<')[1]
                tmp = tmp.split(',')[0]
                if tmp=='std::basic_string':
                    tmp='std::string'
                argument_types[0] = 'std::list'
                argument_types[1] = tmp                
                to_write += "%s<%s>"%(argument_types[0],argument_types[1])
            elif argument_types[1]=='*' and len(argument_types)==2:
                #Case: GEOM_Engine* theEngine
                to_write += "%s%s %s"%(argument_types[0],argument_types[1],argument_name)
            elif len(argument_types)==3: #ex: Handle_WNT_GraphicDevice const &
                to_write += "%s %s %s%s"%(argument_types[1],argument_types[0],argument_types[2],argument_name)
            elif (len(argument_types)==2 and argument_types[1]!="&"):#ex: Aspect_Handle const
                to_write += "%s %s %s"%(argument_types[1],argument_types[0],argument_name)
            elif len(argument_types)==4:
                to_write += "%s %s%s"%(argument_types[0],argument_types[1],argument_name)
            else:
                if ('Standard_Real &' in argument_type) or ('Quantity_Parameter &' in argument_type): # byref Standard_Float parameter
                    to_write += "Standard_Real &OutValue"
                elif 'Standard_Integer &' in argument_type:# byref Standard_Integer parameter
                    to_write += "Standard_Integer &OutValue"
                else:
                    to_write += "%s %s"%(argument_type,argument_name)
            if 'Standard_CString' in to_write:
                to_write = to_write.replace('Standard_CString','char *')
            
            if argument_default_value!="None" and next_argument_default_value!="None":
                # default value may be "1u"or "::AspectCentered" etc.
                if argument_default_value=="1u":
                    argument_default_value = "1"
                elif argument_default_value=="0u":
                    argument_default_value = "0"
                elif argument_default_value.startswith('::'):
                    argument_default_value = argument_default_value[2:]
                to_write += "=%s"%argument_default_value

            is_first = False
        if mem_fun.decl_string.endswith(" const"):
            to_write += ") const;\n"
        else:
            to_write += ");\n"
        if to_write in self._CURRENT_CLASS_EXPOSED_METHODS: #to avoid writing twice constructors
            return True
        if "&arg0);" in to_write: #constructor
            return False
        # dont't write constructors for abstract classes
        if parent_is_abstract and ("%s();"%class_parent_name in to_write):
            return False
        self.fp.write(to_write)
        self._CURRENT_CLASS_EXPOSED_METHODS.append(to_write)     
            
    def process_class(self,class_declaration):
        """
        Process class
        """
        # list with exposed member functions decl_strings
        CURRENT_CLASS_IS_ABSTRACT = False
        self._CURRENT_CLASS_EXPOSED_METHODS = []
        class_name = class_declaration.name
        if class_name in self.ALREADY_EXPOSED:
            return True#raise "Already imported"
        # Check whether the class to process is outside this package
        if class_name.startswith('Handle'):
            from_package = class_name.split('_')[1]
        else:
            from_package = class_name.split('_')[0]
        if from_package!=self.MODULE_NAME:
            self.AddDependency(from_package)
            return True
        if class_declaration.is_abstract: #cannot instanciate abstract class
            CURRENT_CLASS_IS_ABSTRACT = True

        print "####### class %s ##########"%class_name
        # getting docstrings
        if self._generate_doc and not ('Handle' in class_name):
            self.ClassDocstring, self.MemberfunctionDocStrings = BuildDocstring.GetClassDocstrings(class_name)
        # on traite d'abord la classe qui est derivee
        if self.DERIVED.has_key(class_name):
            inherits_from = self.DERIVED[class_name]
            print "\t\tInherits from %s"%inherits_from
            class_to_perform = self._mb.classes(inherits_from).declarations[0]
            if not class_to_perform.name in self.CLASSES_TO_EXCLUDE:
                self.process_class(class_to_perform)
        #
        # Affichage du nom de la classe
        #
        self.fp.write("\n\n%nodefaultctor ")
        self.fp.write("%s;\n"%class_name)
        # docstring for class
        if self._generate_doc and not ('Handle' in class_name):
            self.fp.write('%feature("docstring") ')
            self.fp.write('%s '%class_name)
            self.fp.write('"%s";\n'%self.ClassDocstring)        
        # On verifie si cette classe est derivee d'une autre
        if not self.DERIVED.has_key(class_name):
            self.fp.write("class %s {\n"%class_name)
        else:
            self.fp.write("class %s : public %s {\n"%(class_name,self.DERIVED[class_name]))
        self.fp.write("\tpublic:\n")
        if len(class_declaration.derived)>0:
            for other_classes in class_declaration.derived:
                print "\t\t%s"%other_classes.related_class.name
        print "\t### Member functions for class %s ###"%class_declaration.name
        HAVE_HASHCODE = False
        for mem_fun in class_declaration.public_members:#member_functions():
            # Member functions to exclude
            function_name = mem_fun.name
            if function_name == 'HashCode': #function that have a special HashCode
                nb_arguments = len(mem_fun.arguments)
                if nb_arguments == 1:
                    HAVE_HASHCODE = True
            if (function_name.startswith('~')):#ignore destructor
                pass
            elif not self.MEMBER_FUNCTIONS_TO_EXCLUDE.has_key(class_name):
                self.write_function(mem_fun,CURRENT_CLASS_IS_ABSTRACT)
            elif function_name not in self.MEMBER_FUNCTIONS_TO_EXCLUDE[class_name]:
                 self.write_function(mem_fun,CURRENT_CLASS_IS_ABSTRACT)
        self.fp.write("\n};")
        #
        # Adding a method GetObject() to Handle_* classes
        #
        if (class_name.startswith('Handle_')):
            self.fp.write("\n%")
            self.fp.write("extend %s {\n"%class_name)
            pointed_class = class_name[7:]
            self.fp.write("\t%s* GetObject() {\n"%pointed_class)
            self.fp.write("\treturn (%s*)$self->Access();\n\t}\n};"%pointed_class)
        #
        # Adding a method GetHandle() to objects managed by handles
        #
        if ('Handle_%s'%class_name) in self.ALREADY_EXPOSED:
            self.fp.write("\n%")
            self.fp.write("extend %s {\n"%class_name)
            handle_class_name = 'Handle_%s'%class_name
            self.fp.write("\t%s GetHandle() {\n"%handle_class_name)
            self.fp.write("\treturn *(%s*) &$self;\n\t}\n};"%handle_class_name)
        #
        # Overload __hash__() method for objects that inherits from Standard_Transient
        #
        if (('Handle_%s'%class_name in self.ALREADY_EXPOSED) or HAVE_HASHCODE):
            self.fp.write("\n%")
            self.fp.write("extend %s {\n"%class_name)
            handle_class_name = 'Handle_%s'%class_name
            self.fp.write("\tStandard_Integer __hash__() {\n")
            #self.fp.write("\treturn $self->HashCode(LONG_MAX);\n\t}\n};")
            self.fp.write("\treturn $self->HashCode(__PYTHONOCC_MAXINT__);\n\t}\n};")
        #
        # Or for functions that have a special HashCode function (TopoDS, Standard_GUID etc.)
        #
        # Customize destructor
        self.fp.write('\n%')
        self.fp.write('extend %s {\n'%class_name)
        self.fp.write('\t~%s() {\n\tchar *__env=getenv("PYTHONOCC_VERBOSE");\n\tif (__env){printf("## Call custom destructor for instance of %s\\n");}'%(class_name,class_name))
        self.fp.write('\n\t}\n};')
        #
        # On l'ajoute a la liste des classes deja exposees
        #
        self.ALREADY_EXPOSED.append(class_name)
        global nb_exported_classes
        nb_exported_classes += 1
    
    def IsTypeDef(self,param_name):
        """
        Return True if the param_name is a typedef
        """
        if param_name in self._typedef_list:
            return True
        else:
            return False
    
    def IsEnum(self,param_name):
        """
        Return True if param_name is an enum
        """
        if param_name in self._enum_list:
            return True
        else:
            return False
        
    def CheckParameterIsTypedef(self,param_name):
        """
        Check if the parameter is a typedef defined in this scope or not.
        If this is a typedef that is not defined in that module, returns the module name.
        """
        if self.IsTypeDef(param_name) or self.IsEnum(param_name):
            if param_name.startswith('Handle'):
                return param_name.split("_")[1]
            else:
                return param_name.split("_")[0]            
        return False
                
    def InitBaseSwigFile(self):
        # create OCC.i script
        self.occ_fp = open(os.path.join(os.getcwd(),'%s'%environment.SWIG_FILES_PATH_MODULAR,'%s.i'%self.MODULE_NAME),"w")
        self.WriteLicenseHeader(self.occ_fp)
        self.occ_fp.write("%module ")
        self.occ_fp.write("%s"%self.MODULE_NAME)
        self.occ_fp.write(PYOCC_HEADER_TEMPLATE)
        # Add dependencies
        self.occ_fp.write("\n%%include %s_dependencies.i\n\n"%self.MODULE_NAME)
        # Add headers
        self.occ_fp.write("\n%%include %s_headers.i\n\n"%self.MODULE_NAME)
        
    def FindClasseToExclude(self):
        """
        Build a list about classes to exclude in the whole module
        """
        self.CLASSES_TO_EXCLUDE += self.MODULES[2]
    
    def FindMemberFunctionsToExclude(self):
        """
        Build a dict about members functions to exclude (linkage issue for example)
        """
        if len(self.MODULES)==4:
            self.MEMBER_FUNCTIONS_TO_EXCLUDE.update(self.MODULES[3])
    
    def OSFilterHeaders(self,HXX_FILES):
        """
        Under Linux/MacOS, remove all WNT*headers
        Under Windows, remove all X11/Xfw headers
        """
        # First define all headers that raise a gccxml/pygccxml exception
        HXX_TO_EXCLUDE = ['TCollection_AVLNode.hxx',
                          'BndLib_Compute.hxx','W32_Allocator.hxx',
                          'WNT_Allocator.hxx','WNT_FontMapEntry.hxx',
                          'Standard_Atomic.hxx',
                          'WNT_FontTable.hxx',
                          'AlienImage_GIFLZWDict.hxx','Image_PixelFieldOfDIndexedImage.hxx',
                          'Standard_Transient_proto.hxx',
                          'TopOpeBRepBuild_Builder.hxx','TopOpeBRepBuild_Fill.hxx',
                          'TopOpeBRepBuild_SplitSolid.hxx','TopOpeBRepBuild_SplitShapes.hxx',
                          'TopOpeBRepBuild_SplitEdge.hxx',
                          'Message_Algorithm.hxx',
                          'Message_ExecStatus.hxx',
                          ]
        if sys.platform!='win32':
            HXX_TO_EXCLUDE.append('InterfaceGraphic_Visual3d.hxx') #error with gccxml under Linux
            HXX_TO_EXCLUDE.append('Xw_Cextern.hxx')
        # Also remove all headers that contain 'Test' (for instance BOPTest.hxx').
        # These are just unit tests and missing from Debian Package
        if self.MODULE_NAME!='TopBas':
            for hxx_file in HXX_FILES:
                if 'Test' in hxx_file:
                    HXX_TO_EXCLUDE.append(hxx_file)
        # Under Linux, remove all *WNT* classes
        if sys.platform != 'win32':
            for hxx_file in HXX_FILES:
                if 'WNT' in hxx_file:
                    HXX_TO_EXCLUDE.append(hxx_file)
        # Under Windows, remove all X11/Xfw headers
        elif sys.platform == 'win32':
            for hxx_file in HXX_FILES:
                if ('X11' in hxx_file) or ('XWD' in hxx_file):
                    HXX_TO_EXCLUDE.append(hxx_file)
        if len(HXX_FILES)==0:
            HXX_FILES = CaseSensitiveGlob(os.path.join(self.INC_PATH,'%s*.hxx'%self.MODULE_NAME))
        # Exclude undesired hxx for OS specific or pygccxml issues
        for hxx_to_exclude in HXX_TO_EXCLUDE:
            to_exclude = os.path.join(self.INC_PATH,'%s'%hxx_to_exclude)
            if to_exclude in HXX_FILES:
                HXX_FILES.remove(to_exclude)
        return HXX_FILES
        
    def Init(self):
        """
        Module builder initialization
        """        
        self.HXX_FILES = CaseSensitiveGlob(os.path.join(self.INC_PATH,'%s_*.hxx'%self.MODULE_NAME))+\
                         CaseSensitiveGlob(os.path.join(self.INC_PATH,'%s.hxx'%self.MODULE_NAME))+\
                         CaseSensitiveGlob(os.path.join(self.INC_PATH,'Handle_%s_*.hxx'%self.MODULE_NAME))
        self.HXX_FILES = self.OSFilterHeaders(self.HXX_FILES)
        print " %i headers - GCCXML parsing"%len(self.HXX_FILES)
        # Include additionnal headers
        print self.ADDITIONAL_HEADERS
        for additional_header in self.ADDITIONAL_HEADERS:
            self.ADDITIONAL_HXX += CaseSensitiveGlob(os.path.join(self.INC_PATH,'%s*.hxx'%additional_header))       
        self.ADDITIONAL_HXX = self.OSFilterHeaders(self.ADDITIONAL_HXX)
        ### TO OPTIMIZE
        if self.INC_PATH == environment.SALOME_GEOM_INC:
            # Include additionnal headers
            for additional_header in self.ADDITIONAL_HEADERS:
                self.ADDITIONAL_HXX += CaseSensitiveGlob(os.path.join(environment.OCC_INC,'%s*.hxx'%additional_header))       
                self.ADDITIONAL_HXX = self.OSFilterHeaders(self.ADDITIONAL_HXX)
        # Sorting headers
        self.HXX_FILES.sort()
        self.ADDITIONAL_HXX.sort()
        
    def GenerateWrapper(self):
        """
        Create .hxx file that will be processed with pygccxml
        """
        hxx_wrapper = open(self._wrapper_filename,"w")
        hxx_wrapper.write("// HXX wrapper generated by pythonOCC generate_code.py script.\n")
        hxx_wrapper.write("#ifndef __%s_wrapper__\n#define __%s_wrapper__\n\n"%(self.MODULE_NAME,self.MODULE_NAME))
        for hxx_file in self.HXX_FILES:
            hxx_wrapper.write('#include "%s"\n'%hxx_file)
        hxx_wrapper.write("\n#endif __%s_wrapper__\n"%(self.MODULE_NAME))
        hxx_wrapper.close()
        #
        # Careful: if the module to parse is SGEOM then must parse GEOM classes
        #
        if self.MODULE_NAME == 'SGEOM':
            self.MODULE_NAME = 'GEOM'
        
    def WriteModuleEnums(self):
        """
        Including enums that match module name
        """
        try: #BRepBndLib raises a pygccxml exception.
            for enum in self._mb.enumerations():       
                if enum.name.startswith('%s_'%self.MODULE_NAME):#self.MODULE_NAME in enum.name:
                    enum_name = enum.name
                    enum_values = enum.values
                    self.fp.write("enum %s {\n"%enum_name)
                    for value in enum.values:
                        self.fp.write("\t%s,\n"%value[0])
                    self.fp.write("\t};\n\n")
        except:
            print "Error while getting enums"
    
    def WriteModuleTypedefs(self):
        """
        Including enums that match module name
        """
        if self.MODULE_NAME== 'OSD':
            return # TODO: Problem with a typedef in OSD module
        typedefs = self._mb.global_ns.typedefs()
        for elem in typedefs:
            if (elem.name.startswith('%s_'%self.MODULE_NAME)) and (not '::' in '%s'%elem.type):
                self.fp.write('typedef %s %s;\n'%(elem.type,elem.name))
        self.fp.write('\n')
        
    def BuildModule(self):
        """
        Generate _mb with pygccxml
        """
        self._mb = module_builder.module_builder_t(
                files=[self._wrapper_filename],
                gccxml_path=environment.GCC_XML_PATH,
                define_symbols=environment.PYGCCXML_DEFINES,
                include_paths=[self.INC_PATH, environment.SWIG_FILES_PATH_MODULAR, environment.OCC_INC])
        # Excluding member functions that cause compilation fail
        #if self.MODULE_NAME == 'ShapeSchema':
        #    member_functions = self._mb.member_functions(lambda decl : decl.name.startswith('SAdd'))
        #    member_functions.exclude()
    
if __name__ == '__main__':
    a = glob.glob(os.path.join(self.INC_PATH,'STandard_*.hxx'))
    b = CaseSensitiveGlob(os.path.join(self.INC_PATH,'STandard_*.hxx'))
    assert a == 76
    assert b == 0
    