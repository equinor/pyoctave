PyOctave
====

PyOctave is a simple python wrapper for running octave code from python.

```python
    from pyOctave import Octave
    with Octave() as oct:
         oct.zeros(3) # returns array([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])
```

See docstring of [pyOctave.Octave](src/pyoctave/__init__.py#L50) for more examples.

Inspired by https://github.com/blink1073/oct2py.
