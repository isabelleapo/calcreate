from .utilities import *
import subprocess as sp

class Turbomole:

    def __init__(self,
                 name,
                 smiles,
                 func='b3-lyp',
                 basis='DZP',
                 charge=0,
                 #kwd_dict={'rpas':5},
                 solvent_epsilon=None,
                 xtb=False
                 ):

        self.name = name
        self.smiles = smiles
        self.func = func
        self.basis = basis
        self.charge = charge
        #self.kwd_dict = kwd_dict
        self.solvent_epsilon = solvent_epsilon
        self.xtb = xtb

        try:
            os.makedirs(self.name)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def generate_input(self):
        with cd(self.name):
            pipe = self._generate_pipe()
            generate_xyz(self.smiles, self.xtb)
            self._generate_coord()
            self._define(pipe)
            if self.solvent_epsilon is not None:
                self._add_solvent()

    def _define(self, pipe):
        p = sp.Popen(['define'], stdout=sp.PIPE, stdin=sp.PIPE)
        o, e = p.communicate(pipe.encode())

    def _generate_pipe(self):
        pipe = '\n\na coord\nired\n*\nb all '
        pipe += self.basis
        pipe += '\n*\neht\n\n'
        pipe += str(self.charge)
        pipe += '\n\n\nscf\niter\n300\n\ndft\non\nfunc\n'
        pipe += self.func
        pipe += '\n\n*\n'
        return pipe

    def _generate_coord(self):
        p = sp.Popen(['x2t', 'xyz'], stdout=sp.PIPE, encoding='utf8')
        o, e = p.communicate()
        with open('coord', 'w') as f:
            f.write(o)

    def _add_solvent(self):
        with open('control') as f:
            control = ''.join(f.readlines()[:-1])
        control += '$cosmo\nepsilon={}\n$end'.format(self.solvent_epsilon)
        with open('control', 'w') as f:
           f.write(control)
