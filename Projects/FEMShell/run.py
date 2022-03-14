import subprocess, sys

# Intel MKL number of threads
numThreads = '16'
baseCommand = 'export MKL_NUM_THREADS=' + numThreads + '\nexport OMP_NUM_THREADS=' + numThreads + '\nexport VECLIB_MAXIMUM_THREADS=' + numThreads + '\n'
script = sys.argv[1] + '.py' #'knot.py'

runCommand = baseCommand + 'python3 ' + script
subprocess.call([runCommand], shell=True)

