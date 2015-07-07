#!/usr/bin/env python

'''
Name        : DTM2MESH
Author      : Jonathan Lurie
Email       : lurie.jo@gmail.com
Date        : 2015 06 06
Version     : 0.1
Licence     : MIT
description : Generates a 3D Collada mesh from a Digital Terrain Model (DTM)
              Image.

              This is not for production, since performances could be enhanced.
              In this purpose, it is better not to use DTM of size higher than
              1000x1000.

'''

import sys
import argparse
import numpy as np

import cv2
import collada

# number of meters/pixel for input DTM image
DEFAULT_GROUND_RESOLUTION = 90.

description ="""

Generates a 3D Collada mesh from a Digital Terrain Model (DTM) Image.
This is not for production, since performances could be enhanced.
In this purpose, it is better not to use DTM of size higher than 1000x1000.
"""

def main():

    # Deals with app arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-input', required=True, help='Input DTM image file')
    parser.add_argument('-output', required=True, help='Output Collada file')
    parser.add_argument('-resolution', type=int, required=False, default=DEFAULT_GROUND_RESOLUTION, help='Ground resolution of DTM, in m/pixel. (Default : 90, SRTM compliant)')
    args = parser.parse_args()

    inputDTM = args.input
    outputDAE = args.output
    groundResolution = args.resolution


    # -1 arg means read image as is, instead of forcing 8bit RGB
    img = cv2.imread(inputDTM, -1)

    # finding extremas
    arrayMin = np.amin(img)
    arrayMax = np.amax(img)

    # for keeping aspect ratio
    img = img / groundResolution



    xSize = img.shape[1]
    ySize = img.shape[0]

    zSize = np.amax(img)

    vertices = np.array([])
    triangles = np.array([])
    normales = np.array([])

    progressStatus = None

    # PART 1:
    # loops for computing the vertices positions
    for iy in range(0, ySize-1):

        print "vertices : " + str(round(float(iy)/float(ySize)*100., 2)) + "%"

        # temporary array, just to avoid Numping jamming with too big arrays
        # TODO : improve this part using a better compromise
        tmpVertices = np.array([])

        for ix in range(0, xSize-1):

            # first row
            if(ix == 0 and iy == 0):
                a = np.array([ ix, iy, img[ix, iy] ])
                b = np.array([ ix+1, iy, img[ix+1, iy] ])
                c = np.array([ ix+1, iy+1, img[ix+1, iy+1] ])
                d = np.array([ ix, iy+1, img[ix, iy+1] ])
                tmpVertices = np.append(tmpVertices, [a, b, c, d])

            elif(iy == 0):
                b = np.array([ ix+1, iy, img[ix+1, iy] ])
                c = np.array([ ix+1, iy+1, img[ix+1, iy+1] ])
                tmpVertices = np.append(tmpVertices, [b, c])

            elif(ix == 0):
                c = np.array([ ix+1, iy+1, img[ix+1, iy+1] ])
                d = np.array([ ix, iy+1, img[ix, iy+1] ])
                tmpVertices = np.append(tmpVertices, [c, d])

            else:
                c = np.array([ ix+1, iy+1, img[ix+1, iy+1] ])
                tmpVertices = np.append(tmpVertices, [c])

        vertices = np.append(vertices, tmpVertices)

        # flushing console progress
        sys.stdout.write("\033[F")

    vertices.shape = (-1, 3)

    # number of vertices after the first row
    firtRowSum = (xSize * 2) - 1


    # PART 2:
    # loops for computing triangles.
    # A triangle is made of 3 vertices, but we rather use indexes of vertices
    # than vertices coordinates themselves (Collada specs are like that...)
    for iy in range(0, ySize-1):
        print "triangles : " + str(round(float(iy)/float(ySize)*100., 2)) + "%"

        # temporary array, just to avoid Numping jamming with too big arrays
        # TODO : improve this part using a better compromise
        tmpTriangles = np.array([])

        for ix in range(0, xSize-1):

            # (0, 0)
            if(ix == 0 and iy == 0):
                aIndex = 0
                bIndex = 1
                cIndex = 2
                dIndex = 3

            # (1, 0)
            elif(ix == 1 and iy == 0):
                aIndex = ix
                bIndex = (ix * 2) + 2
                cIndex = (ix * 2) + 3
                dIndex = ((ix-1) * 2) + 2

            # (0, 1)
            elif(ix == 0 and iy == 1):
                aIndex = 3
                bIndex = 2
                cIndex = firtRowSum + 1
                dIndex = firtRowSum + 2

            # (1, 1)
            elif(ix == 1 and iy == 1):
                aIndex = 2
                bIndex = 5
                cIndex = firtRowSum + 3
                dIndex = firtRowSum + 1

            # 1st row (except 1st col)
            elif(iy == 0):
                aIndex = ix * 2
                bIndex = (ix * 2) + 2
                cIndex = (ix * 2) + 3
                dIndex = ((ix-1) * 2) + 3

            # 2nd row (except 1st and 2nd col)
            elif(iy == 1):
                aIndex = (ix * 2) + 1
                bIndex = (ix * 2) + 3
                cIndex = firtRowSum + 2 + ix
                dIndex = firtRowSum + 1 + ix

            # 1st col (except 1st and 2nd row)
            elif(ix == 0):
                aIndex = firtRowSum + (iy - 2) * xSize + 2
                bIndex = firtRowSum + (iy - 2) * xSize + 1
                cIndex = firtRowSum + (iy - 1) * xSize + 1
                dIndex = firtRowSum + (iy - 1) * xSize + 2

            # 2nd col (except 1st and 2nd row)
            elif(ix == 1):
                aIndex = firtRowSum + (iy - 2) * xSize + 1
                bIndex = firtRowSum + (iy - 2) * xSize + 3
                cIndex = firtRowSum + (iy - 1) * xSize + 3
                dIndex = firtRowSum + (iy - 1) * xSize + 1

            # all other cases
            else:
                aIndex = firtRowSum + xSize * (iy - 2) + ix + 1
                bIndex = firtRowSum + xSize * (iy - 2) + ix + 2
                cIndex = firtRowSum + xSize * (iy - 1) + ix + 2
                dIndex = firtRowSum + xSize * (iy - 1) + ix + 1


            # Add triangle T1, vertices a, b, c
            t1 = np.array([ aIndex, bIndex, cIndex ])
            tmpTriangles = np.append(tmpTriangles, t1)

            # Add triangle T2, vertices a, c, d
            t2 = np.array([ aIndex, cIndex, dIndex ])
            tmpTriangles = np.append(tmpTriangles, t2)


            '''
            # This part is dedicated to normal vector computation
            # but not used yet because I didnt find how to use that with PyCollada
            # computation of vectors
            vAB = vertices[bIndex] - vertices[aIndex]
            vAC = vertices[cIndex] - vertices[aIndex]
            vAD = vertices[dIndex] - vertices[aIndex]

            # computation of norm vectors
            t1Norm = computeNormVector(vAB, vAC)
            t2Norm = computeNormVector(vAC, vAD)

            normales = np.append(normales, t1Norm)
            normales = np.append(normales, t2Norm)
            '''

        #
        triangles = np.append(triangles, tmpTriangles)

        # flushing console progress
        sys.stdout.write("\033[F")

    triangles.shape = (-1, 3)

    # Uncomment the following when eventually using normal vectors
    #normales.shape = (-1, 3)

    print("Exporting...")

    # casting npArray to Int was important to garraty compatibility
    # with most softwares
    export_mesh(vertices, triangles.astype(int), outputDAE)



# vA and vB are 3D vectors, in shape of a numpy array
def computeNormVector(vA, vB):
    x = (vA[1] * vB[2]) - (vA[2] * vB[1])
    y = (vA[2] * vB[0]) - (vA[0] * vB[2])
    z = (vA[0] * vB[2]) - (vA[2] * vB[0])

    norm = ((x**2) + (y**2) + (z**2))**0.5

    return np.array([ x/norm, y/norm, z/norm])

# Export the mesh.
# This method is taken from PyMCubes : github.com/pmneila/PyMCubes
# TODO : add normal vectors somewhere
def export_mesh(vertices, triangles, filename, mesh_name="mcubes_mesh"):
    """
    Exports a mesh in the COLLADA (.dae) format.

    Needs PyCollada (https://github.com/pycollada/pycollada).
    """

    mesh = collada.Collada()

    vert_src = collada.source.FloatSource("verts-array", vertices, ('X','Y','Z'))
    geom = collada.geometry.Geometry(mesh, "geometry0", mesh_name, [vert_src])

    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', "#verts-array")


    triset = geom.createTriangleSet(triangles, input_list, "")
    geom.primitives.append(triset)
    mesh.geometries.append(geom)

    geomnode = collada.scene.GeometryNode(geom, [])
    node = collada.scene.Node(mesh_name, children=[geomnode])

    myscene = collada.scene.Scene("mcubes_scene", [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    mesh.write(filename)




# this is quite the main function...
if __name__ == '__main__':
    main()
