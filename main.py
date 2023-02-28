import numpy
import pandas as pd
import csv
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

PV_POINTS = 501
factor_CO2 = (12.011 + 2 * 15.999)/1000
pressure = 1e5

df = pd.read_csv("input/canterafile.csv")

## calc PV
# calc CO2
PV = []
for i in df["CO2"]:
    calc_PV = i / factor_CO2
    PV.append(calc_PV)
df["PV"] = PV

# calc PVs
PVs =[]
for i in df["ProdRate-CO2"]:
    calc_PVs = i * 1000
    PVs.append(calc_PVs)
df["PVs"] = PVs

# calc mu
mu = []
for i in df["viscosity"]:
    calc_mu = i
    mu.append(calc_mu)
df["mu"] = mu

# calc alpha
alpha = []
calc_alpha = df["thermalConductivity"] / df["cp"]
for i in calc_alpha:
     alpha.append(i)
df["alpha"] = alpha

# calc PVNorm
df["PVNorm"] = df["PV"] / df["PV"].max()

# save new csv for evaluation
df.to_csv("all_variables.csv", index=False)

## Interpolation der Werte auf PVtarget Raum
PVtarget = numpy.linspace(0, 1, num=501)

interpolated_df = pd.DataFrame()
for variable in df.columns:
    interpolated_df[variable] = numpy.interp(PVtarget, df["PVNorm"], df[variable])

interpolated_df["psi"] = interpolated_df["rho"] / pressure

## festlegen welche Parameter aus Liste "chose_parameters" geschrieben werden sollen
with open("chose_parameters.csv", newline="") as f:
    reader = csv.reader(f)
    parameter_to_print = list(reader)

# merge the single lists in one big list
parameter_to_print = sum(parameter_to_print, [])

## Datei schreiben
with open("output/tables", "w") as f:
    with open("header/headerTables.txt", "r") as hf:
        header = hf.read()
        f.write(header + "\n")
    for variable in parameter_to_print:
        f.write(variable + "\n")
        f.write(str(PV_POINTS) + "\n")
        f.write("(\n")
        for data in interpolated_df[variable]:
            f.write("{:.12E}\n".format(data))
        f.write(")\n")
        f.write(";\n")

with open("output/scalingParams", "w") as f:
    with open("header/headerScalingParams.txt", "r") as hf:
        header = hf.read()
        f.write(header + "\n")
    f.write("PVmaxScalingTable\n")
    f.write("1\n")
    f.write("{\n")
    f.write("{:.12E}\n".format(max(interpolated_df["PV"])))
    f.write("}")