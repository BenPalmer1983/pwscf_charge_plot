import sys
import os
import numpy
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D




    
if(len(sys.argv) != 6):
  print("How to use:")
  print("python3 plot.py /opt/qe/bin/pp.x /opt/scratch prefix outdir layers")
  print()
  print()
  print("Example:")
  print("python3 plot.py /opt/qe/bin/pp.x /opt/scratch kTNTRDloAmBoYJlu outdir 11")
  exit()

ppbin = str(sys.argv[1]).strip()
scratch = str(sys.argv[2]).strip()
prefix = str(sys.argv[3]).strip()
outdir = str(sys.argv[4]).strip()
layers = int(sys.argv[5].strip())


print("ppbin:      ", ppbin)
print("scratch:    ", scratch)
print("prefix:     ", prefix)
print("outdir:     ", outdir)
print("layers:     ", layers)


if(not os.path.exists(".temp")):
  os.mkdir(".temp") 
if(not os.path.exists(outdir)):
  os.mkdir(outdir) 

for l in range(layers):
  ls = str(l)
  while(len(ls)<4):
    ls = "0" + ls  
  x = l * (1 / (layers - 1))
  fh = open(".temp/"+ls + ".in", 'w')
  fh.write("&inputpp\n")
  fh.write("prefix  = '" + prefix + "'\n")
  fh.write("outdir  = '" + scratch + "',\n")
  fh.write("filplot = '.temp/fil" + ls + ".dat',\n")
  fh.write("plot_num = 0,\n")
  fh.write("spin_component = 0,\n")
  fh.write("/\n")
  fh.write("&plot   \n")
  fh.write("nfile=1,\n")
  fh.write("iflag=2,\n")
  fh.write("output_format=7,\n")
  fh.write("e1(1)=1.0, e1(2)=0.0, e1(3)=0.0,\n")
  fh.write("e2(1)=0.0, e2(2)=1.0, e2(3)=0.0,\n")
  fh.write("x0(1)=0.0, x0(2)=0.0, x0(3)=" + str(x) + ",\n")
  fh.write("nx=200, ny=200\n")
  fh.write("fileout='.temp/" + ls + ".dat',\n")
  fh.write("/\n")
  fh.close()
  cmd = "mpirun -np 4 " + ppbin + " < .temp/"+ls + ".in > .temp/out_" + ls + ".txt"
  os.system(cmd)


for l in range(layers):
  ls = str(l)
  while(len(ls)<4):
    ls = "0" + ls  
  n = 0
  m = 0
  mmax = 0
  fh = open(".temp/"+ls+".dat", 'r')
  for line in fh:
    if(line.strip() == ""):
      n = n + 1
      mmax= max(m, mmax)
      m = 0
    else:
      m = m + 1
      x = float(line[:24])
      y = float(line[24:44])
      z = float(line[44:])
  fh.close()

  d = numpy.zeros((n, mmax),)

  n = 0
  m = 0
  xmin = None
  xmax = None
  ymin = None
  ymax = None
  fh = open(".temp/"+ls+".dat", 'r')
  for line in fh:
    if(line.strip() == ""):
      n = n + 1
      m = 0
    else:
      x = float(line[:24])
      y = float(line[24:44])
      z = float(line[44:])
      if(xmin == None or x < xmin):
        xmin = x
      if(xmax == None or x > xmax):
        xmax = x
      if(ymin == None or y < ymin):
        ymin = y
      if(ymax == None or y > ymax):
        ymax = y
      d[n,m] = z
      m = m + 1
  fh.close()


  x = numpy.linspace(xmin, xmax, n)
  y = numpy.linspace(ymin, ymax, mmax)
  x = x * 0.529
  y = y * 0.529

  plt.clf()    
  plt.figure(figsize=(12,8))
  plt.rc('font', family='serif')
  plt.rc('xtick', labelsize='x-small')
  plt.rc('ytick', labelsize='x-small')
  plt.xticks(fontsize=9)
  #fig, axs = plt.subplots(1, 1, figsize=(12,9))
  #cf = axs.contourf(x, y, d, 128)
  levels = numpy.linspace(0,0.1,128)
  cf = plt.contourf(x, y, d, levels=levels, cmap='coolwarm')
  plt.colorbar(cf)
  plt.savefig('outdir/layer' + ls + '.eps', format='eps')
  plt.savefig('outdir/layer' + ls + '.png', format='png')
  plt.close('all')  

os.system("ffmpeg -pix_fmt yuv420p -r 15 -i outdir/layer%04d.png -codec:v libx264 -preset slow -crf 18 -f mp4 -y outdir/movie.mp4")