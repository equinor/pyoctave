import tempfile
from subprocess import call

import scipy.io as sio


def run_octave(infile, outfile, fun, *args):
    kwargs = {f"i{i}": arg for i, arg in enumerate(args)}
    m_arg = ", ".join(kwargs.keys())
    m_script = f"{fun}({m_arg})"
    ev = f"""load('{infile}');
             is_builtin = exist("{fun}", "builtin");
             if is_builtin == 5,
                nargs = 1;
             else
                nargs = nargout(@{fun});
             end
             out = cell(nargs,1);
             if nargs > 1,
               [out{{:}}] = {m_script};
             else
               out = {m_script};
             end
             save -mat '{outfile}' out nargs;
             """
    sio.savemat(infile, kwargs)
    ret = call(["octave-cli", "--silent", "--eval", ev])
    if ret != 0:
        raise RuntimeError()

    matf = sio.loadmat(outfile)

    if matf["nargs"] > 1:
        return tuple(x[0] for x in matf["out"])
    return matf["out"]


class Octave:
    """
    The Octave object has functions available in Octave as methods.

    >>> oct = Octave()
    >>> oct.zeros(3)
    array([[0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.]])
    """

    def __getattr__(self, fun):
        class Runner:
            def __call__(self, *args):
                ret = None
                with tempfile.NamedTemporaryFile(suffix=".mat") as infile:
                    with tempfile.NamedTemporaryFile(suffix=".mat") as outfile:
                        ret = run_octave(infile.name, outfile.name, fun, *args)
                return ret

        return Runner()
