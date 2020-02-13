import re
import shutil
import tempfile

import pexpect

import scipy.io as sio

# Hack: pyoctave listens to the output of octave-cli and expects a uuid to be
# printed to indicate finished commands before sending a new command. The uuid
# could possibly collide with the output of the command, in which case we are
# in trouble.
delimiter_uuid = "bb8ef39c312b11eaab24331cd2ebe18c"
end_of_command_regex = re.compile(f"[^({delimiter_uuid})]*{delimiter_uuid}".encode())


def run_octave(octaver, infile, outfile, fun, *args):
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
             save -mat '{outfile}' out nargs -v7;
    """
    sio.savemat(infile, kwargs)

    for line in ev.splitlines():
        octaver.sendline(line)
        octaver.expect(end_of_command_regex, timeout=None)

    matf = sio.loadmat(outfile)

    if matf["nargs"] > 1:
        return tuple(x[0] for x in matf["out"])
    return matf["out"]


def run_octave_no_ret(octaver, infile, fun, *args):
    kwargs = {f"i{i}": arg for i, arg in enumerate(args)}
    m_arg = ", ".join(kwargs.keys())
    m_script = f"""
    load('{infile}');
    {fun}({m_arg});
    """
    sio.savemat(infile, kwargs)
    for line in m_script.splitlines():
        octaver.sendline(line)
        octaver.expect(end_of_command_regex, timeout=None)


class Octave:
    """
    The Octave object has functions available in Octave as methods.

    >>> with Octave() as oct:
    ...     oct.zeros(3)
    array([[0., 0., 0.],
           [0., 0., 0.],
           [0., 0., 0.]])

    Unfortunately, sometimes returned values must be squeezed as
    datatypes are not fully compatible with python

    >>> with Octave() as oct:
    ...     oct.zeros(1,3)
    array([[0., 0., 0.]])

    Own matlab scripts can be added to the path by

    >>> from os import path
    >>> with Octave() as oct:
    ...    _ = oct.addpath(path.dirname(__file__) + "/../../examples/")
    ...    oct.myFunc()
    array([[0.]])

    """

    def __init__(self):
        if shutil.which("octave-cli") is None:
            raise Exception("Could not find executable octave-cli")

    def __enter__(self):
        self.octaver = pexpect.spawn("octave-cli", ["--silent", "--no-line-editing"])

        # Sets PS1 and PS2 to the uuid which indicates
        # a finished command.
        self.octaver.sendline(f'PS1("{delimiter_uuid}");')
        self.octaver.expect(end_of_command_regex, timeout=None)
        self.octaver.expect(end_of_command_regex, timeout=None)
        self.octaver.sendline(f'PS2("{delimiter_uuid}");')
        self.octaver.expect(end_of_command_regex, timeout=None)
        self.octaver.expect(end_of_command_regex, timeout=None)

        return self

    def __exit__(self, type, value, traceback):
        self.octaver.close()

    def __getattr__(self1, fun):
        class Runner:
            def __call__(self2, *args):
                ret = None
                with tempfile.NamedTemporaryFile(suffix=".mat") as infile:
                    with tempfile.NamedTemporaryFile(suffix=".mat") as outfile:
                        ret = run_octave(
                            self1.octaver, infile.name, outfile.name, fun, *args
                        )
                return ret

        return Runner()

    @property
    def no_return(self1):
        class OuterRunner:
            def __getattr__(self2, fun):
                class Runner:
                    def __call__(self3, *args):
                        ret = None
                        with tempfile.NamedTemporaryFile(suffix=".mat") as infile:
                            ret = run_octave_no_ret(
                                self1.octaver, infile.name, fun, *args
                            )
                        return ret

                return Runner()

        return OuterRunner()
