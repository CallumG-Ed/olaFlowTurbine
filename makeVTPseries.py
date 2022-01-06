import os
import re

def natsort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]

def main():
    cutPlanesDir = "postProcessing/cuttingPlanes/"

    directories = os.listdir(cutPlanesDir)
    directories = [d for d in directories if "series" not in d]
    directories = sorted(directories, key=natsort_key)

    with open(cutPlanesDir+"yplane.vtp.series", 'w') as yf:
        yf.write("{\n")
        yf.write("  \"file-series-version\" : \"1.0\",\n")
        yf.write("  \"files\" : [\n")
    with open(cutPlanesDir+"yplane.vtp.series", 'a') as yf:
        for time in directories:
            if time != directories[-1]:
                yf.write("    { \"name\" : \""+time+"/yplane.vtp\", \"time\" : "+time+" },\n")
            else:
                yf.write("    { \"name\" : \""+time+"/yplane.vtp\", \"time\" : "+time+" }\n")
        yf.write("  ]\n")
        yf.write("}")

    with open(cutPlanesDir+"xplane.vtp.series", 'w') as yf:
        yf.write("{\n")
        yf.write("  \"file-series-version\" : \"1.0\",\n")
        yf.write("  \"files\" : [\n")
    with open(cutPlanesDir+"xplane.vtp.series", 'a') as yf:
        for time in directories:
            if time != directories[-1]:
                yf.write("    { \"name\" : \""+time+"/xplane.vtp\", \"time\" : "+time+" },\n")
            else:
                yf.write("    { \"name\" : \""+time+"/xplane.vtp\", \"time\" : "+time+" }\n")
        yf.write("  ]\n")
        yf.write("}")
    return

if __name__ == "__main__":
    main()
