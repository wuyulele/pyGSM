import numpy as np
import openbabel as ob
import pybel as pb
import options
import ico as ic
import pes
import os
#import grad

class EOpt(object):

    @staticmethod
    def default_options():
        if hasattr(EOpt, '_default_options'): return EOpt._default_options.copy()

        opt = options.Options() 
        opt.add_option(
            key='nsteps',
            value=1,
            required=False,
            allowed_types=[int],
            doc='Number of steps the optimizer will take')

        opt.add_option(
                key='ICoord',
                required=False,
                allowed_types=[ic.ICoord],
                doc='Internal coord class object ')

        opt.add_option(
                key='filepath',
                value='initial0000.xyz',
                required=False,
                allowed_types=[str],
                doc='Path to xyz file')

        opt.add_option(
                key='PES',
                required=True,
                doc='Potential energy surface calculator')

        EOpt._default_options = opt
        return EOpt._default_options.copy()


    @staticmethod
    def from_options(**kwargs):
        return EOpt(EOpt.default_options().set_values(kwargs))

    def __init__(
            self,
            options,
            ):
        """ Constructor """
        self.options = options

        # Cache some useful attributes
        self.nsteps = self.options['nsteps']
        self.ICoord = self.options['ICoord']
        self.filepath = self.options['filepath']
        self.PES = self.options['PES']

        #TODO What is optCG Ask Paul
        self.optCG = False
        self.isTSnode =False


    def make_Hint(self):

        self.newHess = 5
        Hdiagp = []
        for bond in self.ICoord.bonds:
            Hdiagp.append(0.35*self.ICoord.close_bond(bond))
        for angle in self.ICoord.angles:
            Hdiagp.append(0.2)
        for tor in self.ICoord.torsions:
            Hdiagp.append(0.035)

        self.Hintp=np.diag(Hdiagp)
        """
        print(" Hdiagp elements")
        for i in Hdiagp:
            print i
        print(len(Hdiagp))
        print("Hintp matrix")
        print self.Hintp
        """
        
        #TODO should U be size (num_ics,num_ics) or (nicd,num_ics) ASK Paul
        tmp = self.ICoord.U[0:self.ICoord.nicd][:]*Hdiagp
        self.Hint = np.matmul(np.transpose(tmp),self.ICoord.U[0:self.ICoord.nicd][:])
        self.Hinv = np.linalg.inv(self.Hint)

        """
        print("Hint elements")
        print Hint
        """
        if self.optCG==False or self.isTSNode==False:
            print "Not implemented"

    def Hintp_to_Hint(self):
        tmp = np.matmul(self.U,self.Hint)


    def optimize(self):
        #Hintp_to_Hint()
        energy=0.
        xyzfile=os.getcwd()+"/xyzfile.xyz"
        output_format = 'xyz'
        obconversion = ob.OBConversion()
        obconversion.SetOutFormat(output_format)

        opt_molecules=[]
        opt_molecules.append(self.ICoord.mol.OBMol)

        energy = self.PES.getEnergy()
        print("energy is %1.4f" % energy)
        grad = self.PES.getGrad()

        #for n in range(self.nsteps):

        gradq = self.ICoord.grad_to_q(grad)

        #TODO need to calc gradrms and pgradrms  and gradqprim

        with open(xyzfile,'w') as f:
            for mol in opt_molecules:
                f.write(obconversion.WriteString(mol))


if __name__ == '__main__':

    from obutils import *
    from lot import *
    
    filepath="tests/fluoroethene.xyz"
    mol=pb.readfile("xyz",filepath).next()
    ic1=ic.ICoord.from_options(mol=mol)
    ic1.ic_create()
    ic1.bmatp_create()
    ic1.bmatp_to_U()
    ic1.bmat_create()
    
    nocc=23
    nactive=2
    lot=LOT.from_options(calc_states=[(0,0)],nstates=1,filepath=filepath,nocc=nocc,nactive=nactive,basis='6-31gs')
    #lot.cas_from_geom()

    opt = EOpt.from_options(PES=lot,ICoord=ic1,nsteps=1) 
    opt.make_Hint()
    #opt.optimize()

