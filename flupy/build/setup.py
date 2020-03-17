from distutils.core import setup

from mypyc.build import MypycifyBuildExt, mypycify

setup(
    name="mypyc_output",
    ext_modules=mypycify([], ["-m", "fluent.py"]),
    cmdclass={"build_ext": MypycifyBuildExt},
)
