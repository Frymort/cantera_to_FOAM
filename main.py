import numpy
import pandas as pd
import csv
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

factor_CO2 = (12.011 + 2 * 15.999)/1000
df = pd.read_csv("input/canterafile.csv")

def read_and_save_parameters_to_print(filename):
    data = []
    with open(filename, "r") as f:
        parameter_to_print = []

        # read the second line to get the upper limit
        next(f)
        upper_limit = int(next(f).strip())

        # skip the next line to start from line 3, where the first variable is given
        next(f)

        # read lines until we reach the upper limit and write into list "parameter_to_print"
        for i, line in enumerate(f):
            if i >= upper_limit:
                break
            variable = line.strip()
            if data:
                parameter_to_print.append(variable)

    return(parameter_to_print)


def extract_data(file_name, variable_name):
    data = []
    with open(file_name, "r") as f:
        for line in f:
            if variable_name in line:
                items = line.split()
                data.extend(items)

    extracted_data = data[1].replace(";" , "")

    return (extracted_data)

pv_points = float(extract_data("tableProperties", "PVPoints"))
pressure = float(extract_data("tableProperties", "operatingPressure"))

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

## interpolation to PVtarget space
PVtarget = numpy.linspace(0, 1, num=501)

interpolated_df = pd.DataFrame()
for variable in df.columns:
    interpolated_df[variable] = numpy.interp(PVtarget, df["PVNorm"], df[variable])

interpolated_df["psi"] = interpolated_df["rho"] / pressure

# read the required parameters out of "compressibleGasGRI.foam" and write it to list
parameter_to_print = read_and_save_parameters_to_print("compressibleGasGRI.foam")

## Write dataset
with open("output/tables", "w") as f:
    with open("header/headerTables.txt", "r") as hf:
        header = hf.read()
        f.write(header + "\n")
    for variable in parameter_to_print:
        f.write(variable + "\n")
        f.write(str(pv_points) + "\n")
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